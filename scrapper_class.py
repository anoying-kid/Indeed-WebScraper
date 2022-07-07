from bs4 import BeautifulSoup
import asyncio
import aiohttp
from tqdm import tqdm

class IndeedScraper():
    
    # For storing the request
    li= []
    
    # For storing the data
    di= {}
    
    # job variable is used for naming dictionary( di ) key
    job=1
    
    # Constructor getting the required data
    def __init__(self, what, where, page_till):
        self.what= what
        self.where= where
        self.page_till= page_till
    
    
    # This will request the website for getting the page content
    def get_task(self, s):
        task= []
        for page in range(self.page_till):
            page= page*10
            
            # Page url
            url= 'https://in.indeed.com/jobs'
            
            # Url parameters
            query= {
                'q': self.what,
                'l': self.where,
                'start': page
            }
            
            # HTTP headers are widely used during web scraping because they allow access to otherwise blocked information.
            headers= {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"}
            
            # Appending all the request in task list
            task.append(s.get(url, params=query, headers=headers, ssl=False))
        return task

    
    # req() function will ascynchronously request the data from website
    async def req(self):
        
        # Creating the session
        async with aiohttp.ClientSession() as s:
            tasks= self.get_task(s)
            responses= await asyncio.gather(*tasks)
            
            # tqdm() function is used for bars
            for response in tqdm(responses, desc="Extracting Data!"):
                
                # appending() all the request in li list
                self.li.append(await response.text())
                
    # Try and except is used since some of the detail like companyName, companyReq, dateposted aren't there so
    ## instead of getting the error we print jobs without them
    
    # title() function will scrap the title of the jobs
    async def title(self, text, page, job):
        soup= BeautifulSoup(text, 'lxml')
        Title= soup.find_all('td', {"class": "resultContent"})
        for title in Title:
            self.di[f'job{page}{job}']={}
            ti = title.find_next('span').text
            if ti=='new':
                self.di[f'job{page}{job}']['title']=title.find_all('span')[1].text
            else:
                self.di[f'job{page}{job}']['title']=ti
            job+=1
    
    # companyName() function will scrap the company name of the jobs
    async def companyName(self, text, page, job):
        soup=BeautifulSoup(text, 'lxml')
        Title= soup.find_all('div', {'class': 'heading6 company_location tapItem-gutter companyInfo'})
        for title in Title:
            try:
                self.di[f'job{page}{job}']['companyName']= title.find('span',{'class':'companyName'}).text
                self.di[f'job{page}{job}']['companyLocation']= title.find('div',{'class':'companyLocation'}).text
                job+=1
            except KeyError:
                pass
    # companyReq() function will scrap the company requirements of the jobs
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
            
    # datePosted() function will scrap the date when posted
    async def datePosted(self, text, page, job):
        soup=BeautifulSoup(text, 'lxml')
        Title= soup.find_all('span', attrs={'class': 'date'})
        for title in Title:
            try:
                self.di[f'job{page}{job}']['datePosted']= title.text
                job+=1
            except KeyError:
                pass
    
    # getting all the stuff in one place
    async def main(self):
        page=1
        
        # This is done to follow DRY- Don't Repeat Yourself, we have same lines again and again so getattr is used.
        function= ["title", "companyName", "companyReq", "datePosted"]

        tasks=[]
        
        for fun in tqdm(function, desc="Clearing Data..."):
            for text in self.li:
                
                # getattr() method returns the value of the named attribute of an object
                tasks.append(asyncio.create_task(getattr(self, fun)(text, page, self.job) ))
                page+=1
            await asyncio.gather(*tasks)
            page=1

        ## We can print this terminal also
        # for i in self.di:
        #     print('\n')
        #     for j in self.di[i]:
        #         print(f'{j} : {self.di[i][j]}')
        #     print('-----------------------\n')
        
        # also saving the data in txt file
        with open('data.txt', 'w') as w:
            ls = []
            for i in self.di:
                ls.append('\n')
                for j in self.di[i]:
                    ls.append(f"{j.capitalize()} : {self.di[i][j].capitalize()}\n")
                ls.append('-----------------------\n')
            w.write(''.join(ls))

        print(f"Number of jobs available {len(self.di)}")

## Uncomment these lines if running in ide not using jupyter
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
indeed = IndeedScraper(skill, place, page_till)
indeed.run()

data = known_skill(indeed.di, 'Blockchain')
for i in data.values():
    for j,k in i.items():
        print(f'{j}:{k}\n')
    print('\n')