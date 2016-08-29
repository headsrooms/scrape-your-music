# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from py2neo import Graph
from py2neo.ogm import GraphObject, Property, RelatedTo


class Artist(GraphObject):
    __primarykey__ = "name"

    name = Property()


class Genre(GraphObject):
    __primarykey__ = "name"

    name = Property()

    supergenres = RelatedTo("Genre")
    subgenres = RelatedTo("Genre")


class Release(GraphObject):
    __primarykey__ = "title"

    title = Property()
    ranking = Property()
    average_rating = Property()
    number_ratings = Property()
    year = Property()

    created_by = RelatedTo("Artist")
    belong_to = RelatedTo("Genre")


class RymPipeline(object):
    graph = Graph("http://localhost:7474/", password="01041990")

    def process_item(self, item, spider):
        if 'title' in item:
            print('Putting Release in Neo4J: ' + item['title'])
            release = Release()
            release.title = item['title']
            release.ranking = item['ranking']
            release.average_rating = item['average_rating']
            release.number_ratings = item['number_ratings']
            release.year = item['year']

            for artist in item['artists']:
                artist_object = Artist()
                artist_object.name = artist
                release.created_by.add(artist_object)
                self.graph.push(artist_object)

            for genre in item['genres']:
                genre_object = Genre()
                genre_object.name = genre
                release.belong_to.add(genre_object)
                self.graph.push(genre_object)

            self.graph.push(release)
        else:
            if 'supergenres' in item:
                genre_object = Genre.select(self.graph).where(name=item['name']).first()
                for supergenre in item['supergenres']:
                    print(supergenre)
                    supergenre_object = Genre.select(self.graph).where(name=supergenre).first()
                    if not supergenre_object:
                        supergenre_object = Genre()
                        supergenre_object.name = supergenre
                    genre_object.supergenres.add(supergenre_object)
                    self.graph.push(supergenre_object)
                    self.graph.push(genre_object)

            else:
                if 'subgenres' in item:
                    genre_object = Genre.select(self.graph).where(name=item['name']).first()
                    for subgenre in item['subgenres']:
                        print(subgenre)
                        subgenre_object = Genre.select(self.graph).where(name=subgenre).first()
                        if not subgenre_object:
                            subgenre_object = Genre()
                            subgenre_object.name = subgenre
                        genre_object.subgenres.add(subgenre_object)
                        self.graph.push(subgenre_object)
                        self.graph.push(genre_object)
        return item
