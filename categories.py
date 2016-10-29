import argparse
import requests
import xml.etree.ElementTree as ET
import sqlite3

url = 'https://api.sandbox.ebay.com/ws/api.dll'

headers = { 'X-EBAY-API-CALL-NAME': 'GetCategories',
            'X-EBAY-API-APP-NAME': 'EchoBay62-5538-466c-b43b-662768d6841',
            'X-EBAY-API-CERT-NAME': '00dd08ab-2082-4e3c-9518-5f4298f296db',
            'X-EBAY-API-DEV-NAME': '16a26b1b-26cf-442d-906d-597b60c41c19',
            'X-EBAY-API-SITEID': '0',
            'X-EBAY-API-COMPATIBILITY-LEVEL': '861'
}

xmlbase = """
<?xml version="1.0" encoding="utf-8"?>
<GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**PMIhVg**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpaCpQWdj6x9nY+seQ**L0MCAA**AAMAAA**IahulXaONmBwi/Pzhx0hMqjHhVAz9/qrFLIkfGH5wFH8Fjwj8+H5FN4NvzHaDPFf0qQtPMFUaOXHpJ8M7c2OFDJ7LBK2+JVlTi5gh0r+g4I0wpNYLtXnq0zgeS8N6KPl8SQiGLr05e9TgLRdxpxkFVS/VTVxejPkXVMs/LCN/Jr1BXrOUmVkT/4Euuo6slGyjaUtoqYMQnmBcRsK4xLiBBDtiow6YHReCJ0u8oxBeVZo3S2jABoDDO9DHLt7cS73vPQyIbdm2nP4w4BvtFsFVuaq6uMJAbFBP4F/v/U5JBZUPMElLrkXLMlkQFAB3aPvqZvpGw7S8SgL7d2s0GxnhVSbh4QAqQrQA0guK7OSqNoV+vl+N0mO24Aw8whOFxQXapTSRcy8wI8IZJynn6vaMpBl5cOuwPgdLMnnE+JvmFtQFrxa+k/9PRoVFm+13iGoue4bMY67Zcbcx65PXDXktoM3V+sSzSGhg5M+R6MXhxlN3xYfwq8vhBQfRlbIq+SU2FhicEmTRHrpaMCk4Gtn8CKNGpEr1GiNlVtbfjQn0LXPp7aYGgh0A/b8ayE1LUMKne02JBQgancNgMGjByCIemi8Dd1oU1NkgICFDbHapDhATTzgKpulY02BToW7kkrt3y6BoESruIGxTjzSVnSAbGk1vfYsQRwjtF6BNbr5Goi52M510DizujC+s+lSpK4P0+RF9AwtrUpVVu2PP8taB6FEpe39h8RWTM+aRDnDny/v7wA/GkkvfGhiioCN0z48</eBayAuthToken>
  </RequesterCredentials>
</GetCategoriesRequest>
"""

def build(url, data, headers):
    response = requests.post(url, data=data, headers=headers)
    #Initiate connection to sql
    con = sqlite3.connect('a123.db')
    #This loads the tree directly from a string
    tree = ET.ElementTree(ET.fromstring(response.text.encode('utf-8')))
    #The root is at the top of the tree!
    root = tree.getroot()
    #Fetch version
    version = ( root[4].text, )
    with con:
        cur = con.cursor()
        a = cur.execute("SELECT * FROM sqlite_master WHERE name='Version' and type='table';")
        for row in a:
            #Get latest version added to database
            cur.execute("SELECT * FROM Version ORDER BY rowid DESC LIMIT 1;")
            row = cur.fetchone()
            if version == row:
                print("Database is up to date!")
                return()
    #Search for Category Array, get the initial data
    length = len(root.findall('{urn:ebay:apis:eBLBaseComponents}CategoryArray'))
    Categories = []
    if length > 0:
        version = ( root[6].text, )
        for Category in root[4]:
            category = []
            name = Category.find("{urn:ebay:apis:eBLBaseComponents}CategoryName").text
            cid = Category.find("{urn:ebay:apis:eBLBaseComponents}CategoryID").text
            level = Category.find("{urn:ebay:apis:eBLBaseComponents}CategoryLevel").text
            offer = "false"
            a = Category.find("{urn:ebay:apis:eBLBaseComponents}BestOfferEnabled")
            if hasattr(a, 'text'):
                offer = "true"
            parentid = Category.find("{urn:ebay:apis:eBLBaseComponents}CategoryParentID").text
            category.append(name)
            category.append(cid)
            category.append(level)
            category.append(offer)
            category.append(parentid)
            category = tuple(category)
            Categories.append(category)
        Categories = tuple(Categories)
        """
        Initial schema for tuples of tuples
        categories = (
            ('Antiques', '20081', '1', 'true', 20081),
            ('Art', '550', '1', 'true'. 550),
        )
        """
        with con:
            cur = con.cursor()
            cur.execute("DROP TABLE IF EXISTS Categories")
            cur.execute("DROP TABLE IF EXISTS Version")
            cur.execute("CREATE TABLE Version(Version TEXT)")
            cur.execute("INSERT INTO Version(rowid, Version) VALUES(1, ?)", version)
            cur.execute("CREATE TABLE Categories(Name TEXT, Id INT, Level INT, Price TEXT, Parent INT)")
            cur.executemany("INSERT INTO Categories VALUES(?, ?, ?, ?, ?)", Categories)
            print("New tables were fetched!")
        con.close()
        print("Closing database")
        return()

    xml = """
<?xml version="1.0" encoding="utf-8"?>
<GetCategoriesRequest xmlns="urn:ebay:apis:eBLBaseComponents">
  <RequesterCredentials>
    <eBayAuthToken>AgAAAA**AQAAAA**aAAAAA**PMIhVg**nY+sHZ2PrBmdj6wVnY+sEZ2PrA2dj6wFk4GhCpaCpQWdj6x9nY+seQ**L0MCAA**AAMAAA**IahulXaONmBwi/Pzhx0hMqjHhVAz9/qrFLIkfGH5wFH8Fjwj8+H5FN4NvzHaDPFf0qQtPMFUaOXHpJ8M7c2OFDJ7LBK2+JVlTi5gh0r+g4I0wpNYLtXnq0zgeS8N6KPl8SQiGLr05e9TgLRdxpxkFVS/VTVxejPkXVMs/LCN/Jr1BXrOUmVkT/4Euuo6slGyjaUtoqYMQnmBcRsK4xLiBBDtiow6YHReCJ0u8oxBeVZo3S2jABoDDO9DHLt7cS73vPQyIbdm2nP4w4BvtFsFVuaq6uMJAbFBP4F/v/U5JBZUPMElLrkXLMlkQFAB3aPvqZvpGw7S8SgL7d2s0GxnhVSbh4QAqQrQA0guK7OSqNoV+vl+N0mO24Aw8whOFxQXapTSRcy8wI8IZJynn6vaMpBl5cOuwPgdLMnnE+JvmFtQFrxa+k/9PRoVFm+13iGoue4bMY67Zcbcx65PXDXktoM3V+sSzSGhg5M+R6MXhxlN3xYfwq8vhBQfRlbIq+SU2FhicEmTRHrpaMCk4Gtn8CKNGpEr1GiNlVtbfjQn0LXPp7aYGgh0A/b8ayE1LUMKne02JBQgancNgMGjByCIemi8Dd1oU1NkgICFDbHapDhATTzgKpulY02BToW7kkrt3y6BoESruIGxTjzSVnSAbGk1vfYsQRwjtF6BNbr5Goi52M510DizujC+s+lSpK4P0+RF9AwtrUpVVu2PP8taB6FEpe39h8RWTM+aRDnDny/v7wA/GkkvfGhiioCN0z48</eBayAuthToken>
  </RequesterCredentials>
  <DetailLevel>ReturnAll</DetailLevel>
</GetCategoriesRequest>
"""
    #Request the response
    print("Database is outdated or inexistent, downloading data")
    build(url, xml, headers)



def recurse(f, iid):
        con = sqlite3.connect('a123.db')
        cur = con.cursor()
        cur.execute('SELECT * FROM Categories WHERE Parent=?', iid)
        children = cur.fetchall()
        for child in children:
            iid = child[1]
            name = child[0]
            parentid = child[4]
            offer = child[3]
            mystring = """<tr data-tt-id="%s" data-tt-parent-id="%s">
            <td>%s: Click on the icon in front of me to expand this branch.</td>
            <td>%s</td>
        </tr>
        """
            mystring = mystring % (iid, parentid, name, offer)
            mystring = mystring.encode('utf-8')
            f.write(mystring)
            iid = (iid,)
            recurse(f, iid)


def render(n):
    con = sqlite3.connect('a123.db')
    cur = con.cursor()
    cur.execute("SELECT Id from Categories where id=?", (n,))
    a = cur.fetchall()
    if not a:
        print("Category id does not exist")
        return()
    with open(str(n)+".html", "w+") as Htmlfile:
        Htmlfile.write("""<!DOCTYPE html>

    <html>
      <head>
        <meta charset="utf-8">
        <title>jQuery treetable</title>
        <link rel="stylesheet" href="css/screen.css" media="screen" />
        <link rel="stylesheet" href="css/jquery.treetable.css" />
        <link rel="stylesheet" href="css/jquery.treetable.theme.default.css" />
      </head>
      <body>
        <div id="main">
          <h1>PolymathV Challenge</h1>

          <p><b> Can we build faster? </b>  by <a>Juan F. Verhook</a>.</p>

          <table id="example-basic">
            <caption>Ebay Tree Generated + jQuery </caption>
            <thead>
              <tr>
                <th>Tree column</th>
                <th>Best Offer</th>
              </tr>
            </thead>
            <tbody>

            """)
        con = sqlite3.connect('a123.db')
        with con:
            cur = con.cursor()
            #Gets initial parent
            t = (str(n),)
            cur.execute('SELECT * FROM Categories WHERE Id=?', t)
            parent = cur.fetchone()
            iid = parent[1]
            name = parent[0]
            offer = parent[3]
            mystring = """<tr data-tt-id="%s">
                <td>%s: Click on the icon in front of me to expand this branch.</td>
                <td>%s</td>
            </tr>
            """
            mystring = mystring % (iid, name, offer)
            Htmlfile.write(mystring)
            cur.execute('SELECT * FROM Categories WHERE Parent=?', t)
            children = cur.fetchall()
            for child in children[1:]:
                iid = child[1]
                name = child[0]
                parentid = child[4]
                offer = child[3]
                mystring = """<tr data-tt-id="%s" data-tt-parent-id="%s">
                <td>%s: Click on the icon in front of me to expand this branch.</td>
                <td>%s</td>
            </tr>
            """
                mystring = mystring % (iid, parentid, name, offer)
                Htmlfile.write(mystring)
                iid = (iid,)
                recurse(Htmlfile, iid)

            Htmlfile.write("""</tbody>
            </table>
            <script src="bower_components/jquery/dist/jquery.min.js"></script>
            <script src="bower_components/jquery/dist/core.js"></script>
            <script src="bower_components/jquery-ui/ui/widget.js"></script>
            <script src="bower_components/jquery-ui/ui/widgets/mouse.js"></script>
            <script src="bower_components/jquery-ui/ui/widgets/draggable.js"></script>
            <script src="bower_components/jquery-ui/ui/widgets/droppable.js"></script>
            <script src="jquery.treetable.js"></script>
            <script>
              $("#example-basic").treetable({ expandable: true });
              $("#example-basic-static").treetable();
              $("#example-basic-expandable").treetable({ expandable: true });
              $("#example-advanced").treetable({ expandable: true });
              // Highlight selected row
              $("#example-advanced tbody").on("mousedown", "tr", function() {
                $(".selected").not(this).removeClass("selected");
                $(this).toggleClass("selected");
              });
              // Drag & Drop Example Code
              $("#example-advanced .file, #example-advanced .folder").draggable({
                helper: "clone",
                opacity: .75,
                refreshPositions: true, // Performance?
                revert: "invalid",
                revertDuration: 300,
                scroll: true
              });
              $("#example-advanced .folder").each(function() {
                $(this).parents("#example-advanced tr").droppable({
                  accept: ".file, .folder",
                  drop: function(e, ui) {
                    var droppedEl = ui.draggable.parents("tr");
                    $("#example-advanced").treetable("move", droppedEl.data("ttId"), $(this).data("ttId"));
                  },
                  hoverClass: "accept",
                  over: function(e, ui) {
                    var droppedEl = ui.draggable.parents("tr");
                    if(this != droppedEl[0] && !$(this).is(".expanded")) {
                      $("#example-advanced").treetable("expandNode", $(this).data("ttId"));
                    }
                  }
                });
              });
              $("form#reveal").submit(function() {
                var nodeId = $("#revealNodeId").val()
                try {
                  $("#example-advanced").treetable("reveal", nodeId);
                }
                catch(error) {
                  alert(error.message);
                }
                return false;
              });
            </script>
          </body>
        </html>
        """)

parser = argparse.ArgumentParser()
parser.add_argument('--render', metavar='N',type=int, help='Category id to be rooted from', default=1)
parser.add_argument("--rebuild", help="Download categories from ebay if version is outdated", action='store_true')
args = parser.parse_args()
if args.rebuild:
    build(url, xmlbase, headers)
if args.render:
    render(args.render)
