from urllib.request import urlopen
import json
import time
from pprint import pprint
from io import StringIO


# From https://github.com/silverlays/NoIntro-Roms-Downloader/blob/master/archive_platforms.py
platforms_dict = {}
platforms_resp = urlopen(
    "https://archive.org/advancedsearch.php?q=identifier%3Anointro.*&fl%5B%5D=identifier&fl%5B%5D=title&sort%5B%5D=titleSorter+asc&sort%5B%5D=&sort%5B%5D=&rows=2000&page=1&output=json"
)
for platform in json.loads(platforms_resp.read())["response"]["docs"]:
    try:
        platform_updated_time = platform["title"][
            (str(platform["title"]).rfind("(") + 1) : -1
        ]
        platform_updated_time = time.strftime(
            "%d-%m-%Y %H:%M:%S", time.strptime(platform_updated_time, "%Y%m%d-%H%M%S")
        )
        platform["title"] = str(platform["title"])[
            0 : str(platform["title"]).rfind(" (")
        ].removeprefix("[No-Intro] ")
        platform["title"] = f"{platform['title']} ({platform_updated_time})"
        platforms_dict[platform["title"]] = platform["identifier"]
    except Exception as e:
        print(e)
        pass

pprint(platforms_dict)


def generate_platform_html(identifier):
    nointro_url = f"https://archive.org/details/{identifier}?output=json"
    http_resp = urlopen(nointro_url)
    archive_json = json.loads(http_resp.read())
    buff = StringIO()

    for name, value in archive_json["files"].items():
        if value["format"] == "Metadata" or value["format"] == "Archive BitTorrent":
            continue
        clean_name = name.removeprefix("/")
        size = value["size"]
        md5 = value["md5"]
        buff.write(
            f'<tr><td><a href="https://archive.org/download/{identifier}{name}">{clean_name}</a></td><td>{size}</td><td>{md5}</td></tr>\n'
        )

    with open("template.html") as file:
        template = file.read()

    with open(f"{identifier}.html", "w") as file:
        file.write(template.format(nointrotbody=buff.getvalue()))


index_html_template = """
<html><head><title>No-Intro Archives</title></head>
<body>{links}</body>
</html>
"""
links_buff = StringIO()
for k, v in platforms_dict.items():
    generate_platform_html(v)
    links_buff.write(f'<a href="{v}.html">{k}</a><br>')

with open(f"index.html", "w") as file:
    file.write(index_html_template.format(links=links_buff.getvalue()))
