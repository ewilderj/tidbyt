load("render.star", "render")
load("animation.star", "animation")
load("encoding/base64.star", "base64")

MONA_ICON = base64.decode("""
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
""")

def main(config):
    return render.Root(
        render.Box(
            animation.Transformation(
                child = render.Box(render.Image(src = MONA_ICON)),
                duration = 80,
                delay = 0,
                origin = animation.Origin(0.5, 0.5),
                direction = "alternate",
                fill_mode = "forwards",
                keyframes = [
                    animation.Keyframe(
                        percentage = 0.0,
                        transforms = [
                            animation.Scale(0.2, 0.2),
                            animation.Scale(2.0, 2.0),
                            animation.Rotate(360)],
                        curve = "ease_in_out",
                    ),
                    animation.Keyframe(
                        percentage = 1.0,
                        transforms = [
                            # animation.Rotate(-180),
                            animation.Scale(2.0, 2.0),
                            animation.Scale(0.2, 0.2),
                            animation.Rotate(0),
                        ],

                        curve = "ease_in_out",
                    ),

                ],

            )
        ))
