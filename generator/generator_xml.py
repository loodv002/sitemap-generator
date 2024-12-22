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
        xml = f'<?xml version="1.0" encoding="{self.encoding}"?>\n'
        xml += f'<urlset xmlns="{self.xmlns}">\n'
        for url in self.urlset:
            xml += "  <url>\n"
            xml += f"    <loc>{url['loc']}</loc>\n"
            if url['lastmod']:
                xml += f"    <lastmod>{url['lastmod']}</lastmod>\n"
            if url['changefreq']:
                xml += f"    <changefreq>{url['changefreq']}</changefreq>\n"
            if url['priority']:
                xml += f"    <priority>{url['priority']}</priority>\n"
            xml += "  </url>\n"
        xml += "</urlset>"
        return xml

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

        xml = ""
        for url, priority in urlset:
            xml += "  <url>\n"
            xml += f"    <loc>{url}</loc>\n"
            xml += f"    <priority>{priority}</priority>\n"
            xml += "  </url>\n"
        return xml


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

            xml = f'<?xml version="1.0" encoding="{self.encoding}"?>\n'
            xml += f'<urlset xmlns="{self.xmlns}">\n'
            with open("sitemap_new_threads.xml", "w", encoding=self.encoding) as f:
                f.write(xml)
                for p in processes:
                    p.join()
                for i in range(process_num):
                    f.write(shared_list[i])
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
    import time

    file_name = "./urlweight_python.pkl"
    # file_name = "./urlweight_info.pkl"
    # file_name = "./urlweight_nycu.pkl"
    # file_name = "./urlweight_nycu_ann.pkl"

    with open(file_name, "rb") as file:
        urlweight = pickle.load(file)
    
    # test iteration = 1000000
    # urlweight = urlweight * 160
    print("urlweight len:", len(urlweight))


    serial_time = cal_serial_time(urlweight)

    cal_parallel_time(urlweight, 2, serial_time)
    cal_parallel_time(urlweight, 3, serial_time)
    cal_parallel_time(urlweight, 4, serial_time)
    cal_parallel_time(urlweight, 5, serial_time)
    cal_parallel_time(urlweight, 6, serial_time)


