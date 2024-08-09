import requests
from time import sleep
import csv
import random
import re


api_key = 'D5EXpAVV7TzQA41BkPsbJ2cvcFgt3Ujv'
header_dic = {'X-API-KEY': api_key}


def search(item,industry):

    try:
        site = item[2]
        print(site)

        resultCount = 0

        urls = []
        allResults = []

        finalUrls = []
        finalResults = []

        maybeUrls = []
        maybeResults = []

        api_endpoint = 'https://api.serpsbot.com/v2/google/organic-search'

        searchStrings = ['charitable AND community','charity AND community','philanthropy AND community','donation AND community','\"corporate social responsibility\"']

        for searchString in searchStrings:

            params = {
                "query": searchString + ' site:' + site,
                "gl": "US",
                "hl": "en_US",
                "safe": False,
                "device": "desktop",
                "autocorrect": 0,
                "page": 1,
                "pages": 1,
                "verbatim": False,
                "raw_html": False
            }
            response = requests.post(api_endpoint, json=params, headers=header_dic)
            responseJson = response.json()

            if 'meta' in responseJson:
                resultCount = responseJson['meta']['results']

                if resultCount > 0 and 'data' in responseJson and 'organic' in responseJson['data']:
                    result1 = responseJson['data']['organic'][0]
                    if result1['url'] not in urls:
                        allResults.append(result1)
                        urls.append(result1['url'])

                    if resultCount > 1:
                        result2 = responseJson['data']['organic'][1]
                        if result2['url'] not in urls:
                            allResults.append(result2)
                            urls.append(result2['url'])

                    if resultCount > 2:
                        result3 = responseJson['data']['organic'][2]
                        if result3['url'] not in urls:
                            allResults.append(result3)
                            urls.append(result3['url'])


        if len(allResults) > 0:

            isp = None
            exclusionCount = 0

            # Logic to determine if account meets Ideal Sponsor Profile
            titleOrSnippetStartWithPhrases = ['corporate social responsibility','community involvement','charitable giving','community giving','donation request','charitable donation form','charitable request form','grant request form','community sponsorships','sponsorships and donations','in the community','in our community','our charitable foundation','giving back','give back',' foundation','community impact award']
            snippetContainsPhrases = ['sponsorships','corporate giving','corporate social responsibility','believe that giving back','believe in giving back','paid volunteer','community impact award','charitable foundation']

            exclusions = ['facts about donating','ways you can give','charitable remainder trust','estate tax','tax deduction','diversity equity','diversity, equity','dei','charitable giving campaign','employee campaign']

            for link in allResults:

                # Skip URLs that have this content in the URL string itself
                if '//careers.' in link['url'] or '.websites.' in link['url']:
                    exclusionCount += 1
                    continue

                # Skip pages about scholarships
                if 'scholarship' in link['title'].lower():
                    exclusionCount += 1
                    continue

                # If titles contain any of the phrases
                if any(substring in link['title'].lower() for substring in titleOrSnippetStartWithPhrases):
                    isp = True
                    if link['url'] not in finalUrls:
                        finalResults.append(link)
                        finalUrls.append(link['url'])

                # If snippets start with
                if link['snippet'].lower().startswith(tuple(titleOrSnippetStartWithPhrases)):
                    isp = True
                    if link['url'] not in finalUrls:
                        finalResults.append(link)
                        finalUrls.append(link['url'])

                # If snippets contains
                if any(substring in link['snippet'].lower() for substring in snippetContainsPhrases):
                    isp = True
                    if link['url'] not in finalUrls:
                        finalResults.append(link)
                        finalUrls.append(link['url'])

                # If they have an XYZ Cares program in the titles or snippets (intentionally looking for capitalized Cares, not converting to lowercase)
                if ' Cares' in link['title'] or ' Cares' in link['snippet']:
                    isp = True
                    if link['url'] not in finalUrls:
                        finalResults.append(link)
                        finalUrls.append(link['url'])

                # Any number followed by volunteer hours
                if re.search(r'\d volunteer hours',link['snippet'].lower()):
                    isp = True
                    if link['url'] not in finalUrls:
                        finalResults.append(link)
                        finalUrls.append(link['url'])

                # Donated X, donates X or X in donations where X is any number equal to or greater than $100,000
                if 'donates' in link['snippet'].lower():
                    words = link['snippet'].lower().split()
                    i = words.index('donates')
                    if (i+1) < len(words):
                        if re.search(r'\d',words[i+1]):
                            amount = float(words[i+1].replace('$','').replace(',',''))
                            if amount >= 100000:
                                isp = True
                                if link['url'] not in finalUrls:
                                    finalResults.append(link)
                                    finalUrls.append(link['url'])

                if 'donated' in link['snippet'].lower():
                    words = link['snippet'].lower().split()
                    i = words.index('donated')
                    if (i+1) < len(words):
                        if re.search(r'\d',words[i+1]):
                            amount = float(words[i+1].replace('$','').replace(',',''))
                            if amount >= 100000:
                                isp = True
                                if link['url'] not in finalUrls:
                                    finalResults.append(link)
                                    finalUrls.append(link['url'])

                if 'in donations' in link['snippet'].lower():
                    words = link['snippet'].lower().split()
                    i = words.index('donations')
                    if (i-2) > 0:
                        if re.search(r'\d',words[i-2]):
                            amount = float(words[i-2].replace('$','').replace(',',''))
                            if amount >= 100000:
                                isp = True
                                if link['url'] not in finalUrls:
                                    finalResults.append(link)
                                    finalUrls.append(link['url'])


                if any(substring in link['title'].lower() for substring in exclusions) or any(substring in link['snippet'].lower() for substring in exclusions):
                    exclusionCount += 1
                else:
                    if link['url'] not in maybeUrls:
                        maybeResults.append(link)
                        maybeUrls.append(link['url'])

            for link in maybeResults:
                if link['url'] not in finalUrls:
                    finalResults.append(link)
                    finalUrls.append(link['url'])  

            if exclusionCount >= len(allResults):
                isp = False

            if isp is None:

                # For these industries, if we did not detect a positive previously then set ISP as false
                industries = ['Architecture','Engineering','Design','Electronic Manufacturing','Construction']
                if any(substring in industry for substring in industries):
                    isp = False

                # For all other industries, set it based on page count
                else:
                    if resultCount >= 6:
                        isp = True
                    else:
                        isp = False

            item.append(len(finalResults))
            item.append(finalResults)

            print(len(finalResults))
            for link in finalResults:
                print(' ')
                print(link['title'])
                print(link['snippet'])
                print(link['url'])

            print(' ')
            print(isp)
            print(' ')
            if isp:
                item.append(1)
            else:
                item.append(0)

        else:
            print('False')
            item.append(0)
            item.append([])
            item.append(0)

        return item


    except Exception as e:
        print(e)
        print(response)

        item.append(0)
        item.append([])
        item.append(0)
        return item


def main():

    prefix = 'mn_'


    f = open(prefix + 'salesforce_accounts_charity.csv', 'w')
    writer = csv.writer(f)

    writer.writerow(['Account ID','Account Name','Website','Count','Links','Ideal Sponsor Profile','Subscription Status','Sponsor Status'])

    
    # input file columns: Account ID, Website, Account Name, Industry, Employees, Billing State/Province, Sponsor Status

    filename = prefix + 'salesforce_accounts.csv'

    urlsChecked = []

    with open(filename, 'rt', encoding='ISO-8859-1') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        count = 0
        for row in csv_reader:

            if row[1] != 'Website' and row[1] != None and row[1] != '':

                print('row',count)
                website = row[1].lower().replace('https://','').replace('http://','').replace('www.','').replace('careers.','')
                if '/' in website:
                    website = website.split('/')[0]

                if website not in urlsChecked:

                    urlsChecked.append(website)

                    results = search([row[0],row[2],website],row[3])

                    # Create richtext
                    links = ''
                    if len(results[4]) > 0:

                        for link in results[4]:

                            if len(links) > 1:
                                links = links + '<br><br>'

                            links = links + '<u><b>' + link['title'] + '</b></u><br>' + link['snippet'] + '<br><a href=\"' + link['url'] + '\">' + link['url'] + '</a>'

                    results[4] = links

                    results.append('Prospect')
                    results.append('Prospect')

                    writer.writerow(results)

            count += 1
            sleep(1)

            # if count > 100:
            #     break

    f.close()



if __name__ == '__main__':
    main()
