from multiprocessing import Process, Manager
from itertools import islice
import time

class SiteMap:
    
    encoding = 'UTF-8'
    xmlns = 'http://www.sitemaps.org/schemas/sitemap/0.9'

    def __init__(self):
        self.urlset = []

    def add_url(self, loc, lastmod=None, changefreq=None, priority=None):
        url = {
            "loc": loc,
            "lastmod": lastmod,
            "changefreq": changefreq,
            "priority": priority
        }
        self.urlset.append(url)

    def to_string(self):
        xml_lines = []
        xml_lines.append(f'<?xml version="1.0" encoding="{self.encoding}"?>')
        xml_lines.append(f'<urlset xmlns="{self.xmlns}">')
        
        for url in self.urlset:
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{url['loc']}</loc>")
            if url['lastmod']:
                xml_lines.append(f"    <lastmod>{url['lastmod']}</lastmod>")
            if url['changefreq']:
                xml_lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
            if url['priority']:
                xml_lines.append(f"    <priority>{url['priority']}</priority>")
            xml_lines.append("  </url>")
        xml_lines.append("</urlset>")
        return '\n'.join(xml_lines)

    def save(self, filename):
        xml = self.to_string()
        with open(filename, "w", encoding=self.encoding) as f:
            
            f.write(xml)

    def main(self, pages):
        for path, rank in pages:
            self.add_url(path, priority=str(rank))
        self.save("sitemap_new.xml")


class SiteMapParallel:

    encoding = 'UTF-8'
    xmlns = 'http://www.sitemaps.org/schemas/sitemap/0.9'


    def to_string(self, urlset):

        xml_lines = []
        for url, priority in urlset:
            xml_lines.append("  <url>")
            xml_lines.append(f"    <loc>{url}</loc>")
            xml_lines.append(f"    <priority>{priority}</priority>")
            xml_lines.append("  </url>")
        return '\n'.join(xml_lines)


    def worker(self, shared_list, index, pages, start, end):

        sliced_pages = islice(pages, start, end)
        xml = self.to_string(sliced_pages)
        shared_list[index] = xml

    def main(self, pages, process_num):
        num = len(pages) // process_num
        remain = len(pages) % process_num

        with Manager() as manager:
            shared_list = manager.list([0] * process_num)

            processes = []
            for i in range(process_num):
                start = i * num
                end = start + num
                if i == process_num - 1:
                    end += remain

                p = Process(target=self.worker, args=(shared_list, i, pages, start, end))
                processes.append(p)
                p.start()

            xml_head = f'<?xml version="1.0" encoding="{self.encoding}"?>\n'
            xml_head += f'<urlset xmlns="{self.xmlns}">\n'
            with open("sitemap_new_threads.xml", "w", encoding=self.encoding) as f:
                f.write(xml_head)
                
                for i, p in enumerate(processes):
                    p.join()
                    f.write(shared_list[i])
                    f.write('\n')
                
                f.write("</urlset>")



def cal_serial_time(urlweight):
    times = []
    count = 10
    for i in range(count):
        start = time.time()
        sitemap = SiteMap()
        sitemap.main(urlweight)
        end = time.time()
        times.append(end - start)
    print("serial   平均時間:", sum(times) / len(times))
    return sum(times) / len(times)

def cal_parallel_time(urlweight, process_num, serial_time):
    times = []
    count = 10
    print("process_num:", process_num)
    for i in range(count):
        start2 = time.time()
        sitemap2 = SiteMapParallel()
        sitemap2.main(urlweight, process_num)
        end2 = time.time()
        times.append(end2 - start2)

    parallel_time = sum(times) / len(times)

    print("parallel 最快時間:", min(times))
    print("speedup (最快):", serial_time / min(times))
    print("parallel 平均時間:", parallel_time)
    print("speedup (平均):", serial_time / parallel_time)
    print('\n')


if __name__ == "__main__":
    import pickle

    
    file_name = "../data/generator/urlweight_info.nycu.edu.tw.pkl"
    # file_name = "../data/generator/urlweight_www.cs.nycu.edu.tw_oth.pkl"
    # file_name = "../data/generator/urlweight_docs.python.org_only313.pkl"
    # file_name = "../data/generator/urlweight_www.cs.nycu.edu.tw_ann.pkl"
    # file_name = "../data/generator/urlweight_random_100000.pkl"

    with open(file_name, "rb") as file:
        urlweight = pickle.load(file)

    serial_time = cal_serial_time(urlweight)

    cal_parallel_time(urlweight, 2, serial_time)
    cal_parallel_time(urlweight, 3, serial_time)
    cal_parallel_time(urlweight, 4, serial_time)
    cal_parallel_time(urlweight, 5, serial_time)
    cal_parallel_time(urlweight, 6, serial_time)


