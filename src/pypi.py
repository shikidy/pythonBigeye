import requests


class PyPi:

    def __init__(self) -> None:
        self.ses = requests.session()

    @property
    def latest(self):
        data = self.ses.get("https://pypi.org/search/?q=&o=-created&c=Programming+Language+%3A%3A+Python+%3A%3A+3").text
        return ['https://pypi.org/project/' + el.split('"')[0] for el in data.split('href="/project/')[1:]]
    
    def get_likes_amount(self, text) -> int:
        try:
            link = text.split('https://api.github.com/repos/')[1].split('"')[0]
            data = self.ses.get('https://api.github.com/repos/' + link).json()
            return data['stargazers_count']
        except: ...

    def get_project_downloadlink(self, project_link):
        data = self.ses.get(project_link + '#files').text 
        likes = self.get_likes_amount(data)
        if likes and likes > 250: return
        file_path = data.split('class="card file__card"')[1].split('href="')[1].split('"')[0]
        if not 'tar.gz' in file_path: return
        return file_path
    