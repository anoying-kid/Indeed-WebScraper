from bs4 import BeautifulSoup
import asyncio
import aiohttp
from tqdm import tqdm

class Indeedscraper():
    li= []
    di= {}
    job=1

    def __init__(self, what, where, page_till):
        self.what= what
        self.where= where
        self.page_till= page_till
    
    def get_task(self, s):
        task= []
        for page in range(self.page_till):
            page= page*10
            url= 'https://in.indeed.com/jobs'
            query= {
                'q': self.what,
                'l': self.where,
                'start': page
            }
            headers= {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"}
            task.append(s.get(url, params=query, headers=headers, ssl=False))
        return task

    async def req(self):
        async with aiohttp.ClientSession() as s:
            tasks= self.get_task(s)
            responses= await asyncio.gather(*tasks)
            for response in tqdm(responses, desc="Extracting Data!"):
                self.li.append(await response.text())

    async def title(self, text, page, job):
        soup= BeautifulSoup(text, 'lxml')
        Title= soup.find_all('h2', attrs={"class": "jobTitle jobTitle-color-purple"})
        for title in Title:
            self.di[f'job{page}{job}']={}
            self.di[f'job{page}{job}']['title']=title.find_next('span')['title']
            job+=1

    async def companyName(self, text, page, job):
        soup=BeautifulSoup(text, 'lxml')
        Title= soup.find_all('div', attrs={'class': 'heading6 company_location tapItem-gutter'})
        for title in Title:
            try:
                self.di[f'job{page}{job}']['companyName']= title.pre.span.text
                self.di[f'job{page}{job}']['companyLocation']= title.pre.div.text
                job+=1
            except KeyError:
                pass

    async def companyReq(self, text, page, job):
        soup=BeautifulSoup(text, 'lxml')
        Title= soup.find_all('div', attrs={'class': 'job-snippet'})
        for title in Title:
            try:
                self.di[f'job{page}{job}']['companyReq']= f"1) {title.ul.li.text}.\n2) {title.ul.li.find_next('li').text}"
                job+=1
            except KeyError:
                pass
            except AttributeError:
                pass

    async def datePosted(self, text, page, job):
        soup=BeautifulSoup(text, 'lxml')
        Title= soup.find_all('span', attrs={'class': 'date'})
        for title in Title:
            try:
                self.di[f'job{page}{job}']['datePosted']= title.text
                job+=1
            except KeyError:
                pass

    async def main(self):
        page=1
        function= ["title", "companyName", "companyReq", "datePosted"]

        tasks=[]
        for fun in tqdm(function, desc="Clearing Data..."):
            for text in self.li:
                tasks.append(asyncio.create_task(getattr(self, fun)(text, page, self.job) ))
                page+=1
            await asyncio.gather(*tasks)
            page=1

        # for i in self.di:
        #     print('\n')
        #     for j in self.di[i]:
        #         print(f'{j} : {self.di[i][j]}')
        #     print('-----------------------\n')
        
        with open('data.txt', 'w') as w:
            ls = []
            for i in self.di:
                ls.append('\n')
                for j in self.di[i]:
                    ls.append(f"{j.capitalize()} : {self.di[i][j].capitalize()}\n")
                ls.append('-----------------------\n')
            w.write(''.join(ls))

        print(f"Number of jobs available {len(self.di)}")

    def run(self):
        asyncio.run(self.req())
        asyncio.run(self.main())

def unknown_skill(di, word):
    di_unknown = {}
    for i,j in di.items():
        if word not in j['companyReq'] and word not in j['title']:
            di_unknown[i] = j
    return di_unknown

def known_skill(di, word):
    di_known = {}
    for i,j in di.items():
        if word in j['companyReq'] or word in j['title']:
            di_known[i] = j
    return di_known

skill= input("Your profession, skill: ")
place= input("Where you want your job: ")
page_till=int(input("Number of page to extract: "))
indeed = Indeedscraper(skill, place, page_till)
indeed.run()

data = known_skill(indeed.di, 'Blockchain')
for i in data.values():
    for j,k in i.items():
        print(f'{j}:{k}\n')
    print('\n')