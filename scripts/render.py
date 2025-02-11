import json
import os
import sys

from snakemd import Document
from snakemd.generator import InlineText

BASEDIR = os.path.dirname(os.path.abspath(__file__).replace('scripts/', ''))
AWESOME_TYPE = ['opensource', 'companies']


def abspath(*args, os_path=True, separator='/'):
    path = separator.join(args)
    if os_path is True:
        from pathlib import Path

        return str(Path(path))
    return path


def json_validate(filename: str):
    if not os.path.exists(filename):
        raise FileNotFoundError(filename=filename)

    with open(filename) as fh:
        content = json.load(fh)

    return content


def check(loaded: list):
    values = []
    for name, filename in loaded:
        print(f'Check: {name}')
        values.append(json_validate(filename))

    return values


class Readme():
    organization_name = 'italia-opensource'
    repository_name = 'awesome-italia-opensource'

    def __init__(self, name, data, output_path) -> None:
        self.name = name
        self.data = data
        self.output_path = f'{output_path}/README'
        self.doc = Document(self.output_path)

    @property
    def repository_fullname(self):
        return f'{self.organization_name}/{self.repository_name}'

    @property
    def repository_url(self):
        return f'https://github.com/{self.organization_name}/{self.repository_name}'

    def component_website(self):
        self.doc.add_header('Website view', level=4)
        self.doc.add_paragraph('italia-opensource.github.io').insert_link(
            'italia-opensource.github.io', 'https://italia-opensource.github.io/awesome-italia-opensource/')

    def component_maneiner(self):
        self.doc.add_header('Mantained by', level=3)
        self.doc.add_paragraph("""- **[Fabrizio Cafolla](https://github.com/FabrizioCafolla)**
        <a href="https://www.buymeacoffee.com/fabriziocafolla" target="_blank"><img  align="right" src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 30px !important; width: 150px !important" ></a>""")

    def output(self):
        self.doc.output_page()

    def build(self):
        self.title(self.name, len(self.data))
        self.header()
        self.content(self.data)
        self.footer()

    def title(self, title: str, number_of_list_element):
        self.doc.add_header(f'{title} | Italia Opensource')

        self.doc.add_paragraph(f"""
            <img src='https://img.shields.io/badge/list-{number_of_list_element}-green'>
            <img src='https://img.shields.io/github/last-commit/{self.repository_fullname}/main'>
        """)

    def header(self):
        raise NotImplementedError('header not implemented')

    def content(self):
        raise NotImplementedError('header not content')

    def footer(self):
        self.doc.add_header('Contributors', level=3)
        self.doc.add_paragraph(f"""
            <a href="{self.repository_url}/graphs/contributors">
                <img src="https://contrib.rocks/image?repo={self.repository_fullname}" />
            </a>
        """)

        self.doc.add_header('License', level=3)
        self.doc.add_paragraph(
            'The project is made available under the GPL-3.0 license. See the `LICENSE` file for more information.')


class CompaniesReadme(Readme):
    def __init__(self, name, data, output_path) -> None:
        super().__init__(name, data, output_path)

    def header(self):
        self.doc.add_paragraph(
            'Awesome Italia Innovative Companies is a list of italian startups, scale-up and companies that innovate.')
        self.doc.add_paragraph(
            'The repository intends to give visibility to companies and stimulate the community to contribute to growing the ecosystem.')
        self.doc.add_paragraph(
            'Please read the contribution guidelines before opening a pull request or contributing to this repository') \
            .insert_link('contribution guidelines', f'{self.repository_url}/blob/main/CONTRIBUTING.md')

        self.component_maneiner()

    def content(self, data):
        self.doc.add_header('Companies', level=3)

        self.component_website()

        self.doc.add_header('List', level=4)
        table_content_project = []
        companies_name = []

        for item in data:
            name = item.get('name')
            if name in companies_name:
                raise Exception(f'Company {name} already exist')

            description = item.get('description', '')
            if len(description) > 59:
                description = description[0:60] + ' [..]'

            table_content_project.append([
                InlineText(name, url=item.get('site_url')),
                item.get('type'),
                item.get('market'),
                ', '.join(item['tags']),
                description
            ])

            companies_name.append(name)

        self.doc.add_table(
            ['Name', 'Type', 'Market', 'Tags', 'Description'],
            table_content_project
        )


class OpensourceReadme(Readme):
    def __init__(self, name, data, output_path) -> None:
        super().__init__(name, data, output_path)

    def header(self):
        self.doc.add_paragraph(
            'Italia Opensource is a list of open source projects created by Italian companies or developers.')
        self.doc.add_paragraph(
            'The repository intends to give visibility to open source projects and stimulate the community to contribute to growing the ecosystem.')
        self.doc.add_paragraph(
            'Please read the contribution guidelines before opening a pull request or contributing to this repository') \
            .insert_link('contribution guidelines', f'{self.repository_url}/blob/main/CONTRIBUTING.md')
        self.component_maneiner()

    def content(self, data):
        def _repository(repository_platform, repositories_url, license):
            license = f'<img align="right" src="https://img.shields.io/static/v1?label=license&message={license}&color=orange" alt="License">'
            if repository_platform == 'github':
                repositories_url = '/'.join(repository_url.replace(
                    'https://github.com/', '').split('/')[0:2])
                stars = f'<img align="right" src="https://img.shields.io/github/stars/{repositories_url}?label=%E2%AD%90%EF%B8%8F&logo=github" alt="Stars">'
                issues = f'<img align="right" src="https://img.shields.io/github/issues-raw/{repositories_url}" alt="Issues">'
                return f'{stars}<br>{issues}<br>{license}'

            if repository_platform == 'bitbucket':
                repositories_url = '/'.join(repository_url.replace(
                    'https://bitbucket.org/', '').split('/')[0:2])
                issues = f'<img align="right" src="https://img.shields.io/bitbucket/issues-raw/{repositories_url}" alt="Issues">'
                return f'{issues}<br>{license}'

            if repository_platform == 'gitlab':
                repositories_url = '/'.join(repository_url.replace(
                    'https://gitlab.com', '').split('/')[0:2])
                stars = f'<img align="right" src="https://img.shields.io/gitlab/stars/{repositories_url}?label=%E2%AD%90%EF%B8%8F&logo=gitlab" alt="Stars">'
                issues = f'<img align="right" src="https://img.shields.io/gitlab/issues/open-raw/{repositories_url}" alt="Issues">'
                return f'{stars}<br>{issues}<br>{license}'

        self.doc.add_header('Open source projects', level=3)

        self.component_website()

        self.doc.add_header('List', level=4)
        table_content_project = []

        repositories_url = []

        for item in data:
            repository_url = item['repository_url']

            if item.get('repository_url') in repositories_url:
                raise Exception(
                    f"Project {item['name']} ({repository_url}) already exist")

            name = item['name'].title()
            repository = _repository(
                item['repository_platform'], item['repository_url'], item['license'])
            tags = ', '.join(item['tags'])
            description = item.get('description', '')
            if len(description) > 59:
                description = description[0:60] + ' [..]'

            table_content_project.append([
                InlineText(name, url=item.get('site_url')),
                InlineText(repository, url=repository_url),
                tags,
                description
            ])
            repositories_url.append(repository_url)

        self.doc.add_table(
            ['Name', 'Repository', 'Stack', 'Description'],
            table_content_project
        )


def render(type: str):
    if type not in AWESOME_TYPE:
        raise Exception(f'Error type "{type}" not in {AWESOME_TYPE}')

    dirpath = abspath(BASEDIR, 'awesome', type, 'data')

    loaded = []
    for project in os.listdir(dirpath):
        filename = abspath(dirpath, project)

        if not os.path.isfile(filename):
            print(f"Skip render '{filename}'")
            continue

        if not project.endswith('.json'):
            raise Exception(f'File {project} is not json')

        item = (project.replace('.json', ''), filename)

        loaded.append(item)

    loaded = sorted(loaded, key=lambda tup: tup[0])
    return check(loaded)


def main():
    def opensource():
        data = render(type='opensource')
        builder = OpensourceReadme('Awesome Open Source', data, abspath(
            BASEDIR, 'awesome', 'opensource'))
        builder.build()
        builder.output()

    def companies():
        data = render(type='companies')
        builder = CompaniesReadme('Awesome Companies', data, abspath(
            BASEDIR, 'awesome', 'companies'))
        builder.build()
        builder.output()

    opensource()
    companies()


if __name__ == '__main__':
    sys.exit(main())
