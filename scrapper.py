# async and await keyword are used for asynchronous programming, await means to wait till event loop complete
# These are the python library used in the project
# try excpet are used for exception handling,
## here try and except are used beacause some waste content are coming with the data which is hard to precise the scraping the required data, so try except is used for that

from bs4 import BeautifulSoup #this is used for webscraping the data from website
import asyncio # used for asynchronous programming
import aiohttp # getting asynchronous request from website

li= [] # used for storing the request
di= {} # used for the storing the required data
job=1 # for naming the dictionary

# this function will request the data from the website
def get_task(s):
    task= []
    for page in range(page_till):
        page= page*10

        # website url
        url= 'https://in.indeed.com/jobs'

        # website parameters
        query= {
            'q': what,
            'l': where,
            'start': page
        }

        # website headers
        headers= {"User-Agent" : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15"}
        task.append(s.get(url, params=query, headers=headers, ssl=False))
    return task

# this function will request all the data from the website asynchoronously
async def req():

    # creating the clientsession using context manager
    async with aiohttp.ClientSession() as s:

        #getting all the request
        tasks= get_task(s)
        responses= await asyncio.gather(*tasks)
        for response in responses:
            li.append(await response.text())

# For getting the title from the webpage
async def title(text, page, job):
    soup= BeautifulSoup(text, 'lxml')

    # it will find all the h2 header with class name
    Title= soup.find_all('td', {"class": "resultContent"})
    for title in Title:
        di[f'job{page}{job}']={}
        ti = title.find_next('span').text
        if ti=='new':
            di[f'job{page}{job}']['title']=title.find_all('span')[1].text
        else:
            di[f'job{page}{job}']['title']=ti
        job+=1
        # print(title)

# for getting the company name
async def companyName(text, page, job):
    soup=BeautifulSoup(text, 'lxml')
    Title= soup.find_all('div', {'class': 'heading6 company_location tapItem-gutter companyInfo'})
    for title in Title:
        try:
            di[f'job{page}{job}']['companyName']= title.find('span',{'class':'companyName'}).text
            di[f'job{page}{job}']['companyLocation']= title.find('div',{'class':'companyLocation'}).text
            job+=1
        except KeyError:
            pass

# for getting the company requirement from the webpage
async def companyReq(text, page, job):
    soup=BeautifulSoup(text, 'lxml')
    Title= soup.find_all('div', attrs={'class': 'job-snippet'})
    for title in Title:
        try:
            di[f'job{page}{job}']['companyReq']= f"1) {title.ul.li.text}.\n2) {title.ul.li.find_next('li').text}"
            job+=1
        except KeyError:
            pass
        except AttributeError:
            pass

# for getting the dateposted from the webpage
async def datePosted(text, page, job):
    soup=BeautifulSoup(text, 'lxml')
    Title= soup.find_all('span', attrs={'class': 'date'})
    for title in Title:
        try:
            di[f'job{page}{job}']['datePosted']= title.text
            job+=1
        except KeyError:
            pass

# this is main function
async def main():
    page=1
    tasks=[]
    
    # this will get the title
    for text in li:
        tasks.append(asyncio.create_task(title(text, page, job) ))
        page+=1
    
    # asyncio.gather will gather all the task 
    await asyncio.gather(*tasks)

    # this will get the companyname
    page=1
    for text in li:
        tasks.append(asyncio.create_task(companyName(text, page, job) ))
        page+=1

    # asyncio.gather will gather all the task 
    await asyncio.gather(*tasks)
    
    # this will get the company requirements
    page=1
    for text in li:
        tasks.append(asyncio.create_task(companyReq(text, page, job) ))
        page+=1
    
    # asyncio.gather will gather all the task 
    await asyncio.gather(*tasks)

    # this will get the dateposted
    page=1
    for text in li:
        tasks.append(asyncio.create_task(datePosted(text, page, job) ))
        page+=1
        
    # asyncio.gather will gather all the task 
    await asyncio.gather(*tasks)

    # it will print all the data from the dictionary (di)
    for i in di:
        print('\n')
        for j in di[i]:
            print(f'{j} : {di[i][j]}')
        print('-----------------------\n')
    print(len(di))

# enter the skill of the user
what= input("Skills: ")

# enter the location of job need.
where= input("Location: ")

# Number of page to extract from the website
page_till= int(input("Till page: "))

# for running the req function asynchronously
asyncio.run(req())

# for running the main function asynchronously
asyncio.run(main())