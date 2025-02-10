load("render.star", "render")
load("humanize.star", "humanize")

def main(config):
    if config.get("minutes") == None:
        return render.Root(render.Text("No time given"))

    m = int(config.get("minutes"))
    col = "#fff"
    if m < 5:
        col = "#f00"
    else:
        if m < 8:
            col = "#ff0"
        else:
            col = "#0f0"

    if m <= 0:
        timebit = render.Animation(
            children = [
                render.Text(
                    content = "{u}".format(u = humanize.plural(m, "min")),
                    font = "6x13", color = col),
                render.Text(
                    content = ";-(",
                    font = "6x13", color = "#f00")
                ])
    else:
        timebit = render.Text(
            content = "{u}".format(u = humanize.plural(m, "min")),
            font = "6x13", color = col)

    return render.Root(
        delay = 1000,
        child = render.Box(child = render.Column(
            expanded = True,
            main_align = "center",
            cross_align = "center",
            children = [
                render.Text("Time left", font = "6x13", color = "#fff"),
                timebit
            ]
        ))
    )
