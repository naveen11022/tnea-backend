from locust import HttpUser, task, between


class CollegeUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def get_region(self):
        self.client.get("/get_region")

    @task
    def get_branch(self):
        self.client.get("/get_branch")
