from locust import HttpUser, task, between
import jwt
import time

class APIUser(HttpUser):
    wait_time = between(1, 3)  # users wait between requests

    def on_start(self):
        self.token = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJwTDJybVRNUGJDMTFCTmkxcUZleW11ZG1wU3N0c0tnR2YyS256alJMcHJJIn0.eyJleHAiOjE3NTYyMDA0MTIsImlhdCI6MTc1NjE5OTgxMiwianRpIjoiMTVhYjlmNzctZWMzNy00ZGQ0LThlYjEtODI4ZTgzMWRiMWY0IiwiaXNzIjoiaHR0cHM6Ly9hdXRoLmd1YXJkaGF0Lm5ldC9yZWFsbXMvOTYyIiwic3ViIjoiZDYwNjQyNDItNzI5Zi00NjFkLWE5ZTktNWRjNGNkZjM5YjA0IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoic2NjLXdlYi1hcHAiLCJhY3IiOiIxIiwiYWxsb3dlZC1vcmlnaW5zIjpbImh0dHA6Ly9sb2NhbGhvc3Q6NDIwMCJdLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy05NjIiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJzY29wZSI6InByb2ZpbGUgZW1haWwiLCJjbGllbnRIb3N0IjoiNDkuMzcuMjUxLjg3IiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJzZXJ2aWNlLWFjY291bnQtc2NjLXdlYi1hcHAiLCJjbGllbnRBZGRyZXNzIjoiNDkuMzcuMjUxLjg3IiwiY2xpZW50X2lkIjoic2NjLXdlYi1hcHAifQ.A_i6n7wgtR21kC3ktYw0n6o6QN_lEvvq8nSZDNNvVIaz7tLaLZVUsGwy00NHMutpWwzxuSzS6rOx0CT4y_VDm1_DXV27Gx_ZyGlSXFS_Nn99sVo1KzALqfkWj8V7V0DNjywBzu3ehMoKx1v2g_J1kbG4rr0ARTUeAZD77SACeIDSQZ0Qn8hddJBXNgP6D9qUbcIzCWLGA36-83t8iYde-SUBkeGQ35yr6E80trgn0T-ed2UJSwKuuswNirdD1clZaCEk-hnCqPLUAX12lsUzi3gqxeQDUHtnZJ4ZjlJpVl3YuxG16Fp0kgbQtJ5YPdiv8FR-c4ceDuj_gYiakXMsHw"
        
        
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    @task
    def send_query(self):
        self.client.post(
            "/run-agent",  # replace with actual endpoint
            json={"query": "navigate me to worker event details page"},
            headers=self.headers
        )
