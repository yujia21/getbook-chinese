import re

from bs4 import BeautifulSoup
from getbook.core import Book, Parser, Section

BOOK_PATTERN_SLUG = re.compile(r"/book\d+/([\w-]+)/(?:index\.html)?$")
BOOK_PATTERN_ID = re.compile(r"/book\d*/(\d+)/(?:index.html)?$")
BOOK_PATTERN_2 = re.compile(
    r"(?:files\/\w+|wuxia|tuili)"
    r"/\d{4}(?:\d\d)?/(\d+).html$"
)
META_PATTERN = re.compile("作者：(.*)发布时间：(.*)")


class KanunuParser(Parser):
    NAME = "kanunu"
    ALLOWED_DOMAINS = ["www.kanunu8.com"]
    ENCODING = "gbk"

    @classmethod
    def check_url(cls, url):
        return True

    def fetch(self):
        req = self._request(self.url)
        req.encoding = self.ENCODING
        self.content = req.text
        self._dom = None

    def parse(self):
        m = BOOK_PATTERN_SLUG.search(self.url)
        if m:
            return self.parse_book(m.group(1))
        m = BOOK_PATTERN_ID.search(self.url)
        if m:
            return self.parse_book(m.group(1))
        m = BOOK_PATTERN_2.search(self.url)
        if m:
            return self.parse_book(m.group(1))
        return super().parse()

    def parse_book(self, book_id):
        self.fetch()
        uid = f"{self.NAME}-{book_id}"

        title_el = (
            self.dom.select_one(".catalog h1")
            or self.dom.select_one("h1 > strong")
            or self.dom.select_one("h2 > b")
        )
        title = title_el.get_text().strip() if title_el else "Unknown"

        book = Book(uid, title, lang="zh")

        author_el = self.dom.select_one(".catalog .info")
        if author_el:
            author_text = author_el.get_text().strip()
            author_text = re.sub(r"^作者[：:]", "", author_text).strip()
            book.author = author_text
        else:
            for el in self.dom.select("td"):
                text = el.get_text()
                m = META_PATTERN.findall(text)
                if m:
                    group = m[0]
                    book.author = group[0].strip()
                    book.pubdate = group[1].strip()

        for item in self._parse_book_chapters():
            if isinstance(item, Section):
                book.add_section(item)
            else:
                book.chapters.append(item)
        return book

    def parse_lang(self):
        return "zh"

    def parse_publisher(self):
        return "Kanunu"

    def parse_title(self):
        el = self.dom.select_one(".book-content h1")
        if el:
            return el.get_text().strip()
        el = self.dom.find("font")
        if el:
            title = el.get_text()
            title = title.replace("正文", "")
            return title.strip()

    def parse_content(self):
        el = self.dom.select_one("#neirong") or self.dom.select_one(".neirong")
        if el:
            return el
        els = self.dom.select("td > p")
        if len(els) == 1:
            return els[0]
        html = "\n".join([e.decode_contents() for e in els])
        return BeautifulSoup(html, self.SOUP_FEATURES)

    def _parse_book_chapters(self):
        mulu = self.dom.select_one(".mulu-list")
        if mulu:
            for link in mulu.select("li > a"):
                href = link.get("href")
                title = link.get_text().strip()
                href = self.urljoin(href)
                yield {"title": title, "url": href}
            return

        section_elements = self.dom.find_all(
            "tr", attrs={"align": "center", "bgcolor": "#ffffcc"}
        )
        has_section = len(section_elements) > 1
        section = None

        rule = 'table[bgcolor="#d4d0c8"] tr'
        for el in self.dom.select(rule):
            bgcolor = el.get("bgcolor")
            if bgcolor and bgcolor == "#ffffcc" and has_section:
                title = el.get_text()
                section = Section(title=title)
                yield section
                continue

            for link in el.select("td > a"):
                href = link.get("href")
                title = link.get_text()
                href = self.urljoin(href)
                chapter = {"title": title, "url": href}
                if section:
                    section.chapters.append(chapter)
                else:
                    yield chapter
