import requests
import re
import pandas as pd

BASE_URL = "https://api.glovoapp.com/v3/customer/orders-list?offset={0}&limit=100"
AUTH_TOKEN = "eyJraWQiOiJvbGQiLCJhbGciOiJSUzUxMiJ9.eyJpYXQiOjE3MzAxNDAzNDEsImlzcyI6ImF1dGgiLCJleHAiOjE3MzAxNDE1NDEsInJvbGUiOiJBQ0NFU1MiLCJwYXlsb2FkIjoie1widXNlclJvbGVcIjpcIkNVU1RPTUVSXCIsXCJpc1N0YWZmXCI6ZmFsc2UsXCJwZXJtaXNzaW9uR3JvdXBzXCI6W10sXCJjaXR5R3JvdXBzXCI6W10sXCJ1c2VySWRcIjo0NjcxNzA2LFwiZGV2aWNlSWRcIjoyMTY4MTg4ODcwLFwiZ3JhbnRUeXBlXCI6XCJQQVNTV09SRFwifSIsInZlcnNpb24iOiJWMiIsImp0aSI6ImJlMzM5NzM2LTQ0M2ItNDQ1ZC1hYTI0LTRkNmU4N2QxNTgzZiJ9.VDz2_zbk6cscnoQnPcmslz004X_gQw42HcMQRYaS9WqH8HOytcyQGxXRr90o7k8xDYHf1D7bHnNRoetYJjIkidQ8oLO7dMal7UCK-pmYk6eRK29dX2FKqeyDjvcNTvgDU69cSnhrcSFTklMnzeKyT-3G8OI0CdpuhYjN3CluZP3TibtvqpM0PcZNveti0UM3qdVWTeYBWc_sCrIdMHhXmOV4UyfLjsudHfM3pe28ye7Q6ovvMFkz2KSCcCgISjgQ9sTOVCzFzXPbJJ4dneBJcIXdsHKIlj9EnGD5P-NBTKg68n1m8ArmjepQKkDfXyjnE9A-4kbolWS1JOSvzSHyrg"
if not AUTH_TOKEN:
    raise ValueError("Authorization token is missing. Please set 'AUTH_TOKEN'")

headers = {
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

offset = 0
total_sum = 0.0
order_count = 0

def process_orders(orders):
    global total_sum, order_count
    for order in orders:
        footer_left_data = order["footer"]["left"]["data"]
        print("processing orders")
        
        amount = re.search(r"([\d,]+)\sRON", footer_left_data)
        if amount:
            numeric_value = float(amount.group(1).replace(",", "."))
            total_sum += numeric_value
            order_count += 1

def fetch_orders():
    global offset

    while True:
        url = BASE_URL.format(offset)
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            break

        data = response.json()
        
        if data:
            df = pd.json_normalize(data)
            df.to_csv('glovo.csv', index=False)
        
        if "orders" in data:
            process_orders(data["orders"])
        else:
            print("No 'orders' key found in response.")
            break

        next_page = data.get("pagination", {}).get("next")
        if not next_page:
            break
        else:
            offset = next_page.get("offset", offset)

def main():
    fetch_orders()
    average_order_value = total_sum / order_count if order_count > 0 else 0
    print(f"Total sum: {total_sum:.2f} RON")
    print(f"Total number of orders: {order_count}")
    print(f"Average order value: {average_order_value:.2f} RON")

if __name__ == "__main__":
    main()