import json
import os
from datetime import datetime

import dateparser
import pytz
import requests
from flask import Flask, render_template
from flask_caching import Cache

from pretty_date import pretty_date

app = Flask(__name__)

# Caching
cache_config = {"CACHE_TYPE": "simple", "CACHE_DEFAULT_TIMEOUT": 300}
app.config.from_mapping(cache_config)
cache = Cache(app)

USERS_URL = f"{os.environ['APIG_URL']}/users"


def from_timestamp(timestamp) -> datetime:
    if isinstance(timestamp, str):
        timestamp = int(timestamp)
    return datetime.fromtimestamp(timestamp, tz=pytz.UTC)


def process_review_status(review_status):
    if review_status == "True":
        return "ALIVE"
    if review_status == "False":
        return "DEAD"
    return "UNKNOWN"


@cache.cached(key_prefix="get_data")
def get_data():
    data = json.loads(requests.get(url=USERS_URL).text)
    for user_id, user_data in data.items():
        user_data["Metadata"]["UserId"] = user_id
        last_updated = from_timestamp(user_data["Metadata"]["LastUpdated"])
        user_data["Metadata"]["LastUpdated"] = last_updated
        user_data["Metadata"]["LastUpdatedAgo"] = pretty_date(last_updated)
        for review in user_data["Reviews"]:
            review["ReviewDateTimestamp"] = dateparser.parse(review["ReviewDate"]).timestamp()
            last_updated = from_timestamp(review["LastUpdated"])
            review["LastUpdated"] = last_updated
            review["LastUpdatedAgo"] = pretty_date(last_updated)
            review["ReviewStatus"] = process_review_status(review.get("ReviewStatus"))
    return data


@app.route("/user/<user_id>")
def user_page(user_id):
    user_data = get_data()[user_id]
    alive_count, dead_count, unknown_count = (
        len(list(filter(lambda review: review["ReviewStatus"] == "ALIVE", user_data["Reviews"]))),
        len(list(filter(lambda review: review["ReviewStatus"] == "DEAD", user_data["Reviews"]))),
        len(list(filter(lambda review: review["ReviewStatus"] == "UNKNOWN", user_data["Reviews"]))),
    )
    return render_template(
        "user.html",
        user_data=user_data,
        alive_count=alive_count,
        dead_count=dead_count,
        unknown_count=unknown_count,
    )


@app.route("/")
def index():
    data = get_data()
    return render_template("index.html", data=data)
