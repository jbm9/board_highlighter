import json

class AssemblySteps:
    def __init__(self, path):
        self.path = path
        self.steps = []

        f = file(path)
        g = f.read()
        f.close()

        self.steps = json.loads(g)


    def step_components(self):
        return [ d["components"].split(",") for d in self.steps ]


    def gen_html(self, step):
        q = """
          <div class="inset">
            <img src='%(img)s' width=%(dimx)d height=%(dimy)d/><br/>
            <p>%(name)s</p>
          </div>


          <p>%(text)s</p>

          <br clear="all"/>
    """ % step


        if "tocheck" in step:
            q += "<div class='tocheck'><p><b>Things to check:</b></p>\n<ul>\n"


            for c in step["tocheck"]:
                q += "<li>%s</li>" % c

                q += "</ul></div>\n"
                q += "<br clear='all'/>\n\n"


        return q
