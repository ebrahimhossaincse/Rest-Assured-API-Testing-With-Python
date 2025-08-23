import unittest
import requests
import json


# Configuration
BASE_URL = "https://restful-booker.herokuapp.com"
USERNAME = "admin"
PASSWORD = "password123"


class BookingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        cls.token = None
        cls.booking_id = None
        cls.booking_data = {
            "firstname": "Ebrahim",
            "lastname": "Hossain",
            "totalprice": 100,
            "depositpaid": True,
            "bookingdates": {
                "checkin": "2023-01-01",
                "checkout": "2023-01-05"
            },
            "additionalneeds": "Breakfast"
        }

    def test_00_verify_api_available(self):
        """Check if API is reachable"""
        print("\n[0. API AVAILABILITY CHECK]")
        try:
            response = requests.get(BASE_URL, timeout=5)
            print(f"API status: {response.status_code}")
            self.assertEqual(response.status_code, 200,
                             f"API not reachable. Status: {response.status_code}")
            print("API is available and responding")
        except Exception as e:
            self.fail(f"API connection failed: {str(e)}")

    def test_01_authenticate(self):
        """Get authentication token"""
        print("\n[1. AUTHENTICATION]")
        auth_url = f"{BASE_URL}/auth"
        auth_data = {"username": USERNAME, "password": PASSWORD}

        print(f"Endpoint: {auth_url}")
        print(f"Credentials: {json.dumps(auth_data, indent=2)}")

        try:
            response = requests.post(auth_url, json=auth_data, timeout=5)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")

            self.assertEqual(response.status_code, 200,
                             f"Auth failed. Status: {response.status_code}")

            token = response.json().get("token")
            self.assertIsNotNone(token, "No token in response")

            self.__class__.token = token
            print(f"Authentication successful. Token: {token[:5]}...")

        except Exception as e:
            self.fail(f"Authentication failed: {str(e)}")

    def test_02_create_booking(self):
        """Create a test booking"""
        if not self.token:
            self.skipTest("No authentication token available")

        print("\n[2. BOOKING CREATION]")
        booking_url = f"{BASE_URL}/booking"

        print(f"Endpoint: {booking_url}")
        print(f"Booking data: {json.dumps(self.booking_data, indent=2)}")

        try:
            response = requests.post(booking_url, json=self.booking_data, timeout=5)
            print(f"Response status: {response.status_code}")
            print(f"Full response: {response.text}")

            self.assertEqual(response.status_code, 200,
                             f"Create booking failed. Status: {response.status_code}")

            response_data = response.json()
            booking_id = response_data.get("bookingid")

            self.assertIsNotNone(booking_id,
                                 "No bookingid in response. Full response: " + response.text)

            self.__class__.booking_id = booking_id
            print(f"Booking created successfully! ID: {booking_id}")

        except Exception as e:
            self.fail(f"Booking creation failed: {str(e)}")

    def test_03_get_booking(self):
        """Retrieve the created booking"""
        if not self.booking_id:
            self.skipTest("No booking ID available (creation likely failed)")

        print("\n[3. GET BOOKING]")
        booking_url = f"{BASE_URL}/booking/{self.booking_id}"
        print(f"Endpoint: {booking_url}")

        try:
            response = requests.get(booking_url, timeout=5)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")

            self.assertEqual(response.status_code, 200,
                             f"Get booking failed. Status: {response.status_code}")

            booking = response.json()
            self.assertEqual(booking["firstname"], self.booking_data["firstname"],
                             "Firstname doesn't match")
            print("Booking retrieved successfully!")

        except Exception as e:
            self.fail(f"Failed to get booking: {str(e)}")

    def test_04_update_booking(self):
        """Update the booking"""
        if not self.booking_id or not self.token:
            self.skipTest("Missing booking ID or token")

        print("\n[4. UPDATE BOOKING]")
        update_url = f"{BASE_URL}/booking/{self.booking_id}"
        updated_data = self.booking_data.copy()
        updated_data.update({
            "firstname": "UpdatedName",
            "lastname": "UpdatedLastName"
        })

        headers = {"Cookie": f"token={self.token}"}

        print(f"Endpoint: {update_url}")
        print(f"Update data: {json.dumps(updated_data, indent=2)}")

        try:
            response = requests.put(update_url, json=updated_data, headers=headers, timeout=5)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")

            self.assertEqual(response.status_code, 200,
                             f"Update failed. Status: {response.status_code}")

            updated_booking = response.json()
            self.assertEqual(updated_booking["firstname"], "UpdatedName",
                             "Firstname not updated")
            print("Booking updated successfully!")

        except Exception as e:
            self.fail(f"Failed to update booking: {str(e)}")

    def test_05_delete_booking(self):
        """Clean up by deleting the booking"""
        if not self.booking_id or not self.token:
            self.skipTest("Missing booking ID or token")

        print("\n[5. DELETE BOOKING]")
        delete_url = f"{BASE_URL}/booking/{self.booking_id}"
        headers = {"Cookie": f"token={self.token}"}

        print(f"Endpoint: {delete_url}")

        try:
            response = requests.delete(delete_url, headers=headers, timeout=5)
            print(f"Response status: {response.status_code}")
            print(f"Response body: {response.text}")

            self.assertEqual(response.status_code, 201,
                             f"Delete failed. Status: {response.status_code}")

            # Verify deletion
            get_response = requests.get(delete_url)
            self.assertEqual(get_response.status_code, 404,
                             "Booking still exists after deletion")
            print("Booking deleted successfully!")

        except Exception as e:
            self.fail(f"Failed to delete booking: {str(e)}")


if __name__ == '__main__':
    unittest.main()