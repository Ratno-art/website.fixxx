import json
from datetime import datetime

import pymysql
from paho.mqtt import client as mqtt_client


MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "tambak/iot/data"
MQTT_USERNAME = ""
MQTT_PASSWORD = ""
MQTT_CLIENT_ID = "mqtt-to-mysql-tambak"

DB_HOST = "127.0.0.1"
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "tambak_monitoring"
TABLE_NAME = "monitoring_air"

# Nilai pengganti saat sensor analog belum terbaca atau Arduino mengirim 0.
# Catatan: ini nilai default/simulasi, bukan hasil ukur sensor real.
DEFAULT_PH = 7.5
MIN_PH = 7.0
MAX_PH = 8.5
DEFAULT_TDS = 300.0

REQUIRED_COLUMNS = {
    "THROUGHPUT": "FLOAT DEFAULT 0",
    "DELAY": "FLOAT DEFAULT 0",
    "BANDWIDTH": "FLOAT DEFAULT 0",
}


def to_float(value, default=0.0):
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def sensor_value(value, default_value):
    number = to_float(value)
    if number <= 0:
        return default_value
    return number


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def ensure_columns(connection):
    with connection.cursor() as cursor:
        cursor.execute(f"SHOW COLUMNS FROM `{TABLE_NAME}`")
        existing_columns = {row["Field"].upper() for row in cursor.fetchall()}

        for column_name, column_type in REQUIRED_COLUMNS.items():
            if column_name not in existing_columns:
                cursor.execute(
                    f"ALTER TABLE `{TABLE_NAME}` ADD COLUMN `{column_name}` {column_type}"
                )

    connection.commit()


def normalize_payload(data):
    throughput = to_float(data.get("throughput"))
    bandwidth = to_float(data.get("bandwidth", data.get("bandwith")))
    delay = to_float(data.get("delay", data.get("delay_ms")))
    latency = to_float(data.get("latency", data.get("latency_ms")))

    if bandwidth == 0 and throughput > 0:
        bandwidth = throughput
    if latency == 0 and delay > 0:
        latency = delay
    if delay == 0 and latency > 0:
        delay = latency

    ph = clamp(sensor_value(data.get("ph"), DEFAULT_PH), MIN_PH, MAX_PH)
    tds = sensor_value(data.get("tds"), DEFAULT_TDS)

    return {
        "waktu": data.get("waktu") or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "node": data.get("node") or data.get("node_id") or "-",
        "suhu": to_float(data.get("suhu")),
        "tds": tds,
        "ph": ph,
        "throughput": throughput,
        "packet_loss": to_float(data.get("packet_loss", data.get("packet_loss_percent"))),
        "latency": latency,
        "delay": delay,
        "jitter": to_float(data.get("jitter", data.get("jitter_ms"))),
        "bandwidth": bandwidth,
    }


def insert_sensor_data(data):
    query = f"""
        INSERT INTO `{TABLE_NAME}` (
            `HARI & TANGGAL`,
            `NODE`,
            `SUHU`,
            `TDS`,
            `PH`,
            `THROUGHPUT`,
            `PACKET_LOSS`,
            `LATENCY`,
            `DELAY`,
            `JITTER`,
            `BANDWIDTH`
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """

    values = (
        data["waktu"],
        data["node"],
        data["suhu"],
        data["tds"],
        data["ph"],
        data["throughput"],
        data["packet_loss"],
        data["latency"],
        data["delay"],
        data["jitter"],
        data["bandwidth"],
    )

    connection = get_db_connection()
    try:
        ensure_columns(connection)
        with connection.cursor() as cursor:
            cursor.execute(query, values)
        connection.commit()
    finally:
        connection.close()


def on_connect(client, userdata, flags, reason_code, properties=None):
    if reason_code == 0:
        print(f"Terhubung ke MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribe topic: {MQTT_TOPIC}")
    else:
        print(f"Gagal terhubung ke MQTT broker. Kode: {reason_code}")


def on_message(client, userdata, message):
    payload = message.payload.decode("utf-8")
    print(f"Pesan masuk dari {message.topic}: {payload}")

    try:
        raw_data = json.loads(payload)
        data = normalize_payload(raw_data)
        print(f"Data normalisasi: {data}")
        insert_sensor_data(data)
        print("Data berhasil disimpan ke database.")
    except json.JSONDecodeError:
        print("Payload bukan JSON valid.")
    except Exception as error:
        print(f"Gagal menyimpan data: {error}")


def main():
    client = mqtt_client.Client(
        client_id=MQTT_CLIENT_ID,
        callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2,
    )

    if MQTT_USERNAME:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT)
    client.loop_forever()


if __name__ == "__main__":
    main()
