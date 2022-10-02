from collections import defaultdict
from random import shuffle

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import Prefetch

from services.db_tools import dict_fetch_all


class Category(models.Model):
    TOPIC = 'TPC'
    PHRASEBOOK = 'PRSBK'
    ARTICLE = 'ART'
    HANDBOOK = 'HNDBK'
    QUIZ = 'QUIZ'

    TYPE_CHOICES = [
        (TOPIC, 'Topic'),
        (PHRASEBOOK, 'Phrasebook'),
        (ARTICLE, 'Article'),
        (HANDBOOK, 'Handbook'),
        (QUIZ, 'Quiz')
    ]

    proxy_type = None

    title = models.TextField(verbose_name="Название")
    description = models.TextField(verbose_name='Описание')
    parent = models.ForeignKey("self", related_name='child_category', null=True,
                               blank=True, verbose_name="Предыдущая", on_delete=models.SET_NULL)
    slug = models.SlugField(unique=True, db_index=True)
    type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=ARTICLE,
        db_index=True
    )
    image = models.ImageField(verbose_name='Превью картинка', upload_to='preview_images/categories/', null=True,
                              blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return f'{self.type}:{self.title}'

    @classmethod
    def all_with_child_count(cls, type: str | None = None):
        if type is None:
            type = cls.proxy_type
        return cls.objects.filter(type=type).annotate(child_count=models.Count('articles')).all()


class TopicCategory(Category):
    proxy_type = Category.TOPIC

    class Meta:
        verbose_name = 'Темы топиков'
        verbose_name_plural = 'Тема топиков'
        proxy = True


class PhrasesCategory(Category):
    proxy_type = Category.PHRASEBOOK

    class Meta:
        verbose_name = 'Раздел разговорника'
        verbose_name_plural = 'Разделы разговорника'
        proxy = True


class ArticleCategory(Category):
    proxy_type = Category.ARTICLE

    class Meta:
        verbose_name = 'Тема статей'
        verbose_name_plural = 'Темы статей'
        proxy = True


class HandbookCategory(Category):
    proxy_type = Category.HANDBOOK

    class Meta:
        verbose_name = 'Раздел справочника'
        verbose_name_plural = 'Разделы справочника'
        proxy = True

    @staticmethod
    def get_all_topics():
        sql = """
            WITH RECURSIVE topics AS (
                SELECT 
                    id,
                    title,
                    parent_id
                FROM 
                    knowledge_base_category
                WHERE
                    parent_id IS NULL AND type ='HNDBK'

                UNION
                    SELECT 
                    ht.id,
                    ht.title,
                    ht.parent_id
                FROM 
                    knowledge_base_category ht
                JOIN topics t on ht.parent_id = t.id
                WHERE type ='HNDBK'
            ) SElECT 
                    id, title
                FROM
                    topics;
        """
        return dict_fetch_all(sql)

    @classmethod
    def get_topics_with_lessons(cls):
        topics = cls.get_all_topics()
        topic__lessons_map = Lesson.get_topic__lessons_map()

        for topic in topics:
            topic['lessons'] = topic__lessons_map[topic['id']]

        return topics


class QuizCategory(Category):
    proxy_type = Category.QUIZ

    class Meta:
        verbose_name = 'Тема тестов'
        verbose_name_plural = 'Темы тестов'
        proxy = True

    @classmethod
    def all_with_child_count(cls, type: str | None = None):
        if type is None:
            type = cls.proxy_type
        return cls.objects.filter(type=type).annotate(child_count=models.Count('quizzes')).all()


class Article(models.Model):
    title = models.TextField(verbose_name="Название")
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5), ], verbose_name='Рейтинг')
    parent = models.ForeignKey("self", related_name='child_article', null=True,
                               blank=True, verbose_name="Предыдущая", on_delete=models.SET_NULL)
    category = models.ForeignKey("Category", related_name='articles', null=True,
                                 blank=True, verbose_name="Категория", on_delete=models.SET_NULL)
    content = RichTextField()
    slug = models.SlugField(unique=True, db_index=True)
    views = models.PositiveIntegerField(default=0, blank=True)
    time_for_read = models.PositiveIntegerField(validators=[MinValueValidator(1), ])

    image = models.ImageField(verbose_name='Превью картинка', upload_to='preview_images/articles/', null=True,
                              blank=True)

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"

    def __str__(self):
        return f'{self.category.type}_{self.category.title}:{self.title}'

    @classmethod
    def all_in_category(cls, slug):
        return cls.objects.filter(category__slug=slug).all()


class Topic(Article):
    class Meta:
        verbose_name = 'Топик'
        verbose_name_plural = 'Топики'
        proxy = True


class PhrasesArticle(Article):
    class Meta:
        verbose_name = 'Статья разговорника'
        verbose_name_plural = 'Статьи разговорника'
        proxy = True


class Lesson(Article):
    class Meta:
        verbose_name = 'Статья справочника'
        verbose_name_plural = 'Статьи справочника'
        proxy = True

    @staticmethod
    def get_topic__lessons_map():
        topic__ordered_lessons_map = defaultdict(list)
        sql = """
        WITH RECURSIVE lessons AS (
            SELECT 
                id,
                title,
                parent_id,
                topic_id,
                slug
            FROM 
                knowledge_base_article

            JOIN knowledge_base_category ON knowledge_base_category.id = knowledge_base_article.category_id
            WHERE
                parent_id IS NULL AND knowledge_base_category.type ='HNDBK'

            UNION
                SELECT 
                hl.id,
                hl.title,
                hl.parent_id,
                hl.topic_id,
                hl.slug
            FROM 
                knowledge_base_article hl
            JOIN lessons t on hl.parent_id = t.id
            JOIN knowledge_base_category ON knowledge_base_category.id = knowledge_base_article.category_id
            WHERE knowledge_base_category.type ='HNDBK'
        ) SELECT 
                id, title,topic_id,slug
            FROM
                lessons;
        """
        lessons_data = dict_fetch_all(sql)
        for lesson in lessons_data:
            topic__ordered_lessons_map[lesson['topic_id']].append(lesson)

        return topic__ordered_lessons_map


class Quiz(models.Model):
    title = models.TextField(verbose_name="Название")
    rating = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(5), ], verbose_name='Рейтинг')
    category = models.ForeignKey("Category", related_name='quizzes', null=True,
                                 blank=True, verbose_name="Категория", on_delete=models.SET_NULL)
    slug = models.SlugField(unique=True, db_index=True)
    views = models.PositiveIntegerField(default=0, blank=True)
    time_for_read = models.PositiveIntegerField(validators=[MinValueValidator(1), ])

    image = models.ImageField(verbose_name='Превью картинка', upload_to='preview_images/articles/', null=True,
                              blank=True)

    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'


    @classmethod
    def all_in_category(cls, slug):
        return cls.objects.filter(category__slug=slug).all()

    @classmethod
    def get_quiz_article_data(cls, slug: str):
        article = cls.objects.prefetch_related(Prefetch('questions',
                                                        queryset=Question.objects.prefetch_related('answers')
                                                        .order_by('number'),
                                                        to_attr='ordered_questions')) \
            .get(slug=slug)

        quiz_article_data = {'title': article.title,
                             'img_url': article.image.url if article.image else None,
                             'time_for_read': article.time_for_read,
                             'views': article.views,
                             'rating': article.rating,
                             'questions': []}
        for question in article.ordered_questions:
            quiz_article_data['questions'].append(question.get_question_data())

        return quiz_article_data


class Question(models.Model):
    number = models.PositiveIntegerField(validators=[MinValueValidator(1), ])
    content = models.TextField(verbose_name='Содержание')
    article = models.ForeignKey(Article, verbose_name='Тест', on_delete=models.CASCADE, related_name='questions')

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f'{self.article.title}: {self.number} - {self.content}'

    def get_question_data(self):
        data = {'number': self.number, 'content': self.content, 'answers': []}
        answers = list(self.answers.all())
        shuffle(answers)
        for answer in answers:
            data['answers'].append(answer.get_answer_data())

        return data


class Answer(models.Model):
    content = models.TextField(verbose_name='Содержание')
    correct = models.BooleanField(verbose_name='Правильный', default=False)
    question = models.ForeignKey(Question, verbose_name='Вопрос', on_delete=models.CASCADE, related_name='answers')

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = 'Ответы'

    def __str__(self):
        return f'{self.question.content}: {self.content} - {self.correct}'

    def get_answer_data(self):
        return {'content': self.content, 'correct': self.correct}
