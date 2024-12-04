import xml.etree.ElementTree as ET
from xml.dom import minidom

class SiteMap:
    
    urlset = None
    encoding = 'UTF-8'
    xmlns = 'http://www.sitemaps.org/schemas/sitemap/0.9'

    def __init__(self):
        self.urlset = ET.Element("urlset", xmlns=self.xmlns)

    def add_url(self, loc, lastmod=None, changefreq=None, priority=None):
        url = ET.SubElement(self.urlset, "url")
        ET.SubElement(url, "loc").text = loc
        if lastmod:
            ET.SubElement(url, "lastmod").text = lastmod
        if changefreq:
            ET.SubElement(url, "changefreq").text = changefreq
        if priority:
            ET.SubElement(url, "priority").text = priority

    def to_string(self):
        rough_string = ET.tostring(self.urlset, self.encoding)
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")

    def save(self, filename):
        with open(filename, "w") as f:
            f.write(self.to_string())


    def main(self, pages):
        for path, rank in pages:
            self.add_url(path, priority=str(rank))
        self.save("sitemap.xml")

