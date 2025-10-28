from dataclasses import dataclass, field
from lxml import html


@dataclass
class LoadMetrics:
    """Stores the (max - current - min - avg) values for a single SSID."""

    max_clients: int
    current_clients: int
    min_clients: int
    avg_clients: float

    @classmethod
    def zero(cls) -> "LoadMetrics":
        return cls(max_clients=0, current_clients=0, min_clients=0, avg_clients=0.0)


@dataclass
class Load:
    """Aggregates LoadMetrics for all specific SSIDs."""

    all: LoadMetrics
    eduroam: LoadMetrics
    lrz: LoadMetrics
    mwn_events: LoadMetrics
    bayern_wlan: LoadMetrics
    other: LoadMetrics = field(default_factory=LoadMetrics.zero)


@dataclass
class AccessPointData:
    """Stores key information for a single Access Point (AP)."""

    location: str
    room: str
    load: Load


def parse_metrics(value_str: str) -> LoadMetrics:
    """Parses a string like '(024 - 4 - 3 - 8.22)' into a strictly typed LoadMetrics object."""
    cleaned_values = [v.strip() for v in value_str.strip("()").split("-")]

    try:
        max_val = int(cleaned_values[0])
        current_val = int(cleaned_values[1])
        min_val = int(cleaned_values[2])
        avg_val = float(cleaned_values[3])

        return LoadMetrics(
            max_clients=max_val,
            current_clients=current_val,
            min_clients=min_val,
            avg_clients=avg_val,
        )
    except (ValueError, IndexError) as e:
        print(
            f"Warning: Error parsing load metrics '{value_str}'. Using zeroed metrics. Error: {e}"
        )
        return LoadMetrics.zero()


def parse_ap_table(html_content: str) -> list[AccessPointData]:
    """Parses the HTML table and returns a list of AccessPointData objects."""
    tree = html.fromstring(html_content)
    ap_list: list[AccessPointData] = []

    for row in tree.xpath("//tbody/tr"):
        cells = row.xpath("./td")

        ap_list.append(
            AccessPointData(
                location=parse_location(cells[0]),
                room=parse_room(cells[1]),
                load=parse_load(cells[5]),
            )
        )

    return ap_list


def parse_location(cell) -> str:
    location_text = " ".join(cell.xpath(".//text()")).strip().replace("\n", ", ")
    location = " ".join(location_text.split())
    return location


def parse_room(cell) -> str:
    return cell.text_content().strip()


def parse_load(cell) -> Load:
    SSID_KEY_MAP = {
        "Gesamt": "all",
        "eduroam": "eduroam",
        "lrz": "lrz",
        "mwn-events": "mwn_events",
        "@BayernWLAN": "bayern_wlan",
        "Sonstige": "other",
    }

    load_map = {
        "all": LoadMetrics.zero(),
        "eduroam": LoadMetrics.zero(),
        "lrz": LoadMetrics.zero(),
        "mwn_events": LoadMetrics.zero(),
        "bayern_wlan": LoadMetrics.zero(),
        "other": LoadMetrics.zero(),
    }

    load_table = cell.xpath("./table/tr")

    for load_row in load_table:
        html_key = load_row.xpath("./td[1]/text()")[0].strip().replace(":", "")
        value_str = load_row.xpath("./td[2]/text()")[0].strip()

        dataclass_key = SSID_KEY_MAP.get(html_key)
        if dataclass_key:
            load_map[dataclass_key] = parse_metrics(value_str)

    return Load(
        all=load_map["all"],
        eduroam=load_map["eduroam"],
        lrz=load_map["lrz"],
        mwn_events=load_map["mwn_events"],
        bayern_wlan=load_map["bayern_wlan"],
        other=load_map["other"],
    )


# 5. Input HTML Data
html_data = """
<table id="aptable" class="tablesorter">
     <thead>
       <tr><th>Standort</th><th>Raum</th><th>AP-Name</th><th>AP-Status</th><th>AP-Typ</th><th>Auslastung nach SSIDs (max - aktuell - min - avg)</th><th>Auslastung (6 Tage) nach SSIDs (gesamt, eduroam, lrz, mwn-events, @BayernWLAN,  Sonstige)</th></tr>
     </thead>
     <tbody>
       <tr>
          <td><a href="/apstat/filter/Unterbezirk/su">LMU, Jura, Veterinärstr. 1</a><br/>Veterinärstr. 1<br/>80539 München</td>
          <td>401</td><td><a href="/apstat/apa08-4su/">apa08-4su</a></td>
          <td> <font color="green">Online</font> seit 2025-10-16 17:13</td>
          <td><a href="/apstat/filter/Typ/Aruba -&gt; AP-515">Aruba -&gt; AP-515</a></td>
          <td><table><tr><td>Gesamt:    </td> <td>(024 - 4 - 3 - 8.22)</td></tr><tr><td>eduroam:   </td> <td>(019 - 2 - 1 - 5.90)</td></tr><tr><td>lrz: </td> <td>(001 - 1 - 1 - 1.00)</td></tr><tr><td>mwn-events: </td> <td>(000 - 0 - 0 - 0.00)</td></tr><tr><td>@BayernWLAN:</td> <td>(004 - 1 - 1 - 1.32)</td></tr></table></td>
          <td> Graphen sind in der Gesamtansicht deaktiviert </td>
       </tr>
       <tr>
          <td><a href="/apstat/filter/Unterbezirk/q2">TUM, Geb. 4277/4278, Forstwissenschaft, FVA - Forstwissenschaftliche Versuchsanstalt</a><br/>Hans-Carl-von-Carlowitz-Platz 2<br/>85354 Freising</td>
          <td>1.2.2.6, Büro</td><td><a href="/apstat/apa10-2q2/">apa10-2q2</a></td>
          <td> <font color="green">Online</font> seit 2025-10-16 20:48</td>
          <td><a href="/apstat/filter/Typ/Aruba -&gt; AP-505H">Aruba -&gt; AP-505H</a></td>
          <td><table><tr><td>Gesamt:    </td> <td>(017 - 3 - 3 - 6.10)</td></tr><tr><td>eduroam:   </td> <td>(012 - 1 - 1 - 3.91)</td></tr><tr><td>lrz: </td> <td>(002 - 1 - 1 - 1.03)</td></tr><tr><td>mwn-events: </td> <td>(000 - 0 - 0 - 0.00)</td></tr><tr><td>@BayernWLAN:</td> <td>(003 - 1 - 1 - 1.17)</td></tr></table></td>
          <td> Graphen sind in der Gesamtansicht deaktiviert </td>
       </tr>
       <tr>
          <td><a href="/apstat/filter/Unterbezirk/bh">TUM, Geb. 0507 (Stammgelände)</a><br/>Arcisstraße 21<br/>80333 München</td>
          <td>2731, Besprechung m. Küche</td><td><a href="/apstat/apa09-2bh/">apa09-2bh</a></td>
          <td> <font color="green">Online</font> seit 2025-10-16 22:03</td>
          <td><a href="/apstat/filter/Typ/Aruba -&gt; AP-303H">Aruba -&gt; AP-303H</a></td>
          <td><table><tr><td>Gesamt:    </td> <td>(018 - 3 - 3 - 4.92)</td></tr><tr><td>eduroam:   </td> <td>(013 - 1 - 1 - 2.55)</td></tr><tr><td>lrz: </td> <td>(001 - 1 - 1 - 1.00)</td></tr><tr><td>mwn-events: </td> <td>(000 - 0 - 0 - 0.00)</td></tr><tr><td>@BayernWLAN:</td> <td>(004 - 1 - 1 - 1.36)</td></tr></table></td>
          <td> Graphen sind in der Gesamtansicht deaktiviert </td>
       </tr>
       <tr>
          <td><a href="/apstat/filter/Unterbezirk/at">TUM, Geb. 5101, Physikgebäude</a><br/>James-Franck-Straße 1<br/>85748 Garching</td>
          <td>3250</td><td><a href="/apstat/apa03-3at/">apa03-3at</a></td>
          <td> <font color="green">Online</font> seit 2025-10-16 17:13</td>
          <td><a href="/apstat/filter/Typ/Alcatel-Lucent -&gt; OAW-AP325">Alcatel-Lucent -&gt; OAW-AP325</a></td>
          <td><table><tr><td>Gesamt:    </td> <td>(016 - 3 - 3 - 3.90)</td></tr><tr><td>eduroam:   </td> <td>(013 - 1 - 1 - 1.89)</td></tr><tr><td>lrz: </td> <td>(001 - 1 - 1 - 1.00)</td></tr><tr><td>mwn-events: </td> <td>(000 - 0 - 0 - 0.00)</td></tr><tr><td>@BayernWLAN:</td> <td>(002 - 1 - 1 - 1.01)</td></tr></table></td>
          <td> Graphen sind in der Gesamtansicht deaktiviert </td>
       </tr>
       <tr>
          <td><a href="/apstat/filter/Unterbezirk/ig">LMU, Neubau Bauabschnitt 2, Biologie I, Martinsried</a><br/>Großhaderner Str. 2-4<br/>82152 Planegg-Martinsried</td>
          <td>E01.017</td><td><a href="/apstat/apa13-1ig/">apa13-1ig</a></td>
          <td> <font color="green">Online</font> seit 2025-10-16 20:53</td>
          <td><a href="/apstat/filter/Typ/Aruba -&gt; AP-515">Aruba -&gt; AP-515</a></td>
          <td><table><tr><td>Gesamt:    </td> <td>(012 - 3 - 3 - 5.73)</td></tr><tr><td>eduroam:   </td> <td>(010 - 1 - 1 - 3.73)</td></tr><tr><td>lrz: </td> <td>(001 - 1 - 1 - 1.00)</td></tr><tr><td>mwn-events: </td> <td>(000 - 0 - 0 - 0.00)</td></tr><tr><td>@BayernWLAN:</td> <td>(001 - 1 - 1 - 1.00)</td></tr></table></td>
          <td> Graphen sind in der Gesamtansicht deaktiviert </td>
       </tr>
     </tbody>
</table>
"""

# Execute the parsing
access_points = parse_ap_table(html_data)

# Print the Result
print(
    "\n### ✅ Resulting List of AccessPointData Objects with Strict Types and Nested Load ###\n"
)
for ap in access_points:
    print(ap)
