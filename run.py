import datetime
import json
import os

import pandas as pd
import requests
import argparse
from gooey import Gooey, GooeyParser


def create_config_file_if_need():
    if not os.path.exists("config.json"):
        with open("config.json", "w") as f:
            default_args = {
                "accessToken": "",
                "searchKeyword": "",
                "proxyAddress": "",
                "proxyPort": "",
                "proxyUsername": "",
                "proxyPassword": "",
            }
            json.dump(default_args, f)



def get_args():
    create_config_file_if_need()
    with open("config.json", "r") as f:
        default_args = json.load(f)
    parser = GooeyParser(description="GitHub Repository Search")
    parser.add_argument("--accessToken", type=str, required="", default=default_args["accessToken"], help="GitHub Access Token")
    parser.add_argument("--searchKeyword", type=str, required="", default=default_args["searchKeyword"], help="Keyword to search for in GitHub repositories")
    parser.add_argument("--proxyAddress", type=str, default=default_args["proxyAddress"], help="Proxy Address")
    parser.add_argument("--proxyPort", type=str, default=default_args["proxyPort"], help="Proxy Port")
    parser.add_argument("--proxyUsername", type=str, default=default_args["proxyUsername"], help="Proxy Username")
    parser.add_argument("--proxyPassword", type=str, default=default_args["proxyPassword"], help="Proxy Password")
    args = parser.parse_args()
    with open("config.json", "w") as f:
        default_args = vars(args)
        json.dump(default_args, f)
    return args


def replace_special_chars(filename):
    return "".join(["_" if c in ' /\\:*?"<>|' else c for c in filename])


def set_headers(args):
    return {"Authorization": f"token {args.accessToken}"}


def set_params(args):
    return {"q": args.searchKeyword, "page": 1, "per_page": 100}


def set_proxies(args):
    if args.proxyAddress and args.proxyPort:
        if args.proxyUsername and args.proxyPassword:
            return {
                "http": f"http://{args.proxyUsername}:{args.proxyPassword}@{args.proxyAddress}:{args.proxyPort}",
                "https": f"http://{args.proxyUsername}:{args.proxyPassword}@{args.proxyAddress}:{args.proxyPort}",
            }
        else:
            return {
                "http": f"http://{args.proxyAddress}:{args.proxyPort}",
                "https": f"http://{args.proxyAddress}:{args.proxyPort}",
            }
    else:
        return None


def get_response(headers, params, proxies):
    return requests.get("https://api.github.com/search/repositories", headers=headers, params=params, proxies=proxies)


def get_data(response):
    return response.json()


def get_df(data):
    return pd.DataFrame(data["items"], columns=["name", "url", "description"])


def replace_url(df):
    return df["url"].apply(lambda x: x.replace("https://api.github.com/repos", "https://github.com"))


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def get_title(keyword, timestamp):
    return f"{replace_special_chars(keyword)}_{timestamp}"


def write_excel(df, keyword, title):
    writer = pd.ExcelWriter(f"{title}.xlsx", engine="xlsxwriter")
    df.to_excel(writer, sheet_name=keyword, index=False)
    writer.save()


def open_excel(title):
    if os.name == "nt":
        os.system(f'start excel.exe "{title}.xlsx"')
    elif os.name == "posix":
        os.system(f'open "{title}.xlsx"')
    else:
        print("Unsupported OS")


@Gooey
def main():
    args = get_args()
    print("Arguments received successfully!")
    headers = set_headers(args)
    print("Headers set successfully!")
    keyword = args.searchKeyword
    params = set_params(args)
    print("Parameters set successfully!")
    proxies = set_proxies(args)
    print("Proxies set successfully!")
    response = get_response(headers, params, proxies)
    if response.status_code == 200:
        print("Response received successfully!")
        data = get_data(response)
        print("Data extracted successfully!")
        df = get_df(data)
        print("Dataframe created successfully!")
        df["url"] = replace_url(df)
        print("URLs replaced successfully!")
        timestamp = get_timestamp()
        print("Timestamp generated successfully!")
        title = get_title(keyword, timestamp)
        print("Title generated successfully!")
        write_excel(df, keyword, title)
        print("Excel file written successfully!")
        open_excel(title)
        print("Excel file opened successfully!")
        with open("config.json", "w") as f:
            default_args = vars(args)
            json.dump(default_args, f)
    else:
        print("GitHub Network Error:", response.status_code)


if __name__ == "__main__":
    main()
