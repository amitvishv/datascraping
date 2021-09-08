import time

from django.http import HttpResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from .models import  ScrapData
# Create your views here.
def home(request):
    if request.method == 'POST':
        category_name = request.POST.get('cname')
        category_url = request.POST.get('url')
        data = []
        print(category_name, category_url, type(category_name), type(category_url))
        cookies_load = {
            '_jbdisplaymode': '",VM_DISPLAYMESSAGECENTRE"',
            'JSESSIONID': "8BFA43734BF57B72DF74563009ADFC3B.jobsearch75"
        }
        cookies = {
            '_jbdisplaymode': '",VM_DISPLAYMESSAGECENTRE"',
            'JSESSIONID': "7C9F069995307045FB232C5CC82C5988.jobsearch76"
        }
        cookies_sask = {
            'JSESSIONID': "UVrAt4CRQ55oFqjEb2Z7Gk1HL6JO5Ql63H_qbPYc_Cldzyem8ka1!-1736777192",
        }
        if category_name == None or category_name == '':
            data.append(' Category Name')
        if category_url == None or category_url == '':
            data.append(' Category Url')
        if category_url and category_name:
            category = category_name
            url = category_url
            load_url = 'https://www.jobbank.gc.ca/jobsearch/job_search_loader.xhtml'
            html_content = requests.get(url, cookies=cookies).text
            soup = BeautifulSoup(html_content, "lxml")
            total_record = eval(soup.find_all('span', attrs={"class": "found"})[0].text.replace(',', '')) // 25
            print("Total Approx Record----------", total_record * 25)
            result_op = []
            counter = 1
            for i in range(total_record):
                show_more = requests.get(load_url, cookies=cookies_load).text
                show_more_html = BeautifulSoup(show_more, "lxml")
                article = show_more_html.find_all('a', attrs={"class": "resultJobItem"})

                print("Inside First Loop")
                for j in article:
                    main_article_url = j.get('href')
                    if len(ScrapData.objects.filter(scrapped_url="https://www.jobbank.gc.ca" + main_article_url)) >= 1:
                        continue
                    article_data = requests.get("https://www.jobbank.gc.ca" + main_article_url, cookies=cookies).text
                    article_data_html = BeautifulSoup(article_data, "lxml")
                    empolyer_name = ""
                    email_id_empolyer = ""
                    form_data = {
                        "seekeractivity:jobid": "1782791",
                        "seekeractivity_SUBMIT": "1",
                        "javax.faces.ViewState": "stateless",
                        "javax.faces.behavior.event": "action",
                        "jbfeJobId": "1782791",
                        "action": "applynowbutton",
                        "javax.faces.partial.event": "click",
                        "javax.faces.source": "seekeractivity",
                        "javax.faces.partial.ajax": "true",
                        "javax.faces.partial.execute": "jobid",
                        "javax.faces.partial.render": "applynow",
                        "seekeractivity": "seekeractivity",
                    }
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    job_url = ''
                    email_data = ''
                    sask_jobs = article_data_html.find('a', attrs={"id": "externalJobLink"})
                    if sask_jobs:
                        if 'View the full job posting on' in sask_jobs.find('span').text:
                            sask_url = sask_jobs.get('href')
                            sask_result = requests.get(sask_url, cookies=cookies_sask).text
                            sask_html = BeautifulSoup(sask_result, "lxml")
                            emp_details = sask_html.find('div', attrs={'id': 'emp_details'})
                            print(emp_details,"empdetails")
                            try:
                                email_id_empolyer = emp_details.find_all('a')[-1].text
                                empolyer_name = emp_details.find_all('p')[0].text
                                job_url = sask_url
                                email_data = emp_details
                            except:
                                pass
                    try:
                        email_check = article_data_html.find('button', attrs={"id": "applynowbutton"}).text
                        if 'Show how to apply' in email_check:
                            job_id = article_data_html.find('input', attrs={"id": "seekeractivity:jobid"}).get('value')
                            form_data['seekeractivity:jobid'] = job_id
                            form_data['jbfeJobId'] = job_id
                            for k in article_data_html.find_all('span', attrs={"property": "name"}):
                                try:
                                    empolyer_name = k.find('strong').text
                                except:
                                    pass
                                if empolyer_name == '' or empolyer_name == None:
                                    try:
                                        empolyer_name = k.find('a').text
                                    except:
                                        pass
                            email_data = requests.post("https://www.jobbank.gc.ca" + main_article_url, cookies=cookies_load,
                                                       params=form_data).text

                            email_data_html = BeautifulSoup(email_data, "lxml")
                            e_data = email_data_html.find_all('a')
                            email_id_empolyer = "N/A"
                            for e in e_data:
                                try:
                                    if '@' in e.text:
                                        email_id_empolyer = e.text
                                except:
                                    pass
                        job_url = "https://www.jobbank.gc.ca" + main_article_url
                        print(f"Empolyer Name is -->  {empolyer_name}\nEmployer Email is --> {email_id_empolyer}")
                    except Exception as e:
                        print(f"Error occured {e}")
                    try:
                        ScrapData.objects.create(empolyername=empolyer_name, empolyeremail=email_id_empolyer,
                                                 category=category, scrapped_url=job_url, html=email_data)
                        result_op.append([empolyer_name, email_id_empolyer])
                        print(counter)
                        counter += 1
                    except:
                        pass
            print("Success")

        return render(request, "index.html", context={"data": f"Please provide details like: {' '.join(data)} "})
    if request.method == 'GET':
        return render(request, "index.html")

    return HttpResponse("Success")
