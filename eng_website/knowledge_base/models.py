from collections import defaultdict
from random import shuffle, sample

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from ckeditor.fields import RichTextField
from django.db.models import Prefetch, Count
from django.urls import reverse

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
    def all_with_child_count(cls, type = None):
        if type is None:
            type = cls.proxy_type
        return cls.objects.filter(type=type).annotate(child_count=models.Count('articles')).all()


class TopicCategory(Category):
    proxy_type = Category.TOPIC

    class Meta:
        verbose_name = 'Тема топиков'
        verbose_name_plural = 'Темы топиков'
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
                    ht.id,
                    ht.title,
                    ht.parent_id
                FROM 
                    knowledge_base_category ht
                WHERE
                    ht.parent_id IS NULL AND ht.type ='HNDBK'

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

    def get_absolute_url(self):
        pass


class QuizCategory(Category):
    proxy_type = Category.QUIZ

    class Meta:
        verbose_name = 'Тема тестов'
        verbose_name_plural = 'Темы тестов'
        proxy = True

    @classmethod
    def all_with_child_count(cls, type= None):
        if type is None:
            type = cls.proxy_type
        return cls.objects.filter(type=type).annotate(child_count=models.Count('quizzes')).all()


class Article(models.Model):
    title = models.TextField(verbose_name="Название")
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

    @classmethod
    def get_large_feed_data(cls):
        articles = []
        for article in cls.objects.filter(category__type=Category.ARTICLE).order_by('-views')[:3]:
            articles.append({
                'title': article.title,
                'views': article.views,
                'img_url': article.image.url,
                'url': reverse(f'article', kwargs={
                    'category_slug': article.category.slug,
                    'slug': article.slug,

                }),
                'url_section': reverse(f'articles-categories'),
            })

        return articles

    @classmethod
    def get_most_raited_materials_by_sections(cls, count_for_section=4):
        materials_by_sections = {}
        type_section_url_name_pairs = (
            (Category.TOPIC, 'topics', 'topic'), (Category.ARTICLE, 'articles', 'article'),
            (Category.PHRASEBOOK, 'phrasebook', 'phrase-article')
        )
        for type, section, url_name in type_section_url_name_pairs:
            articles = []
            count_db = cls.objects.filter(category__type=type).aggregate(count=Count('id'))['count']
            if count_for_section > count_db:
                queryset = cls.objects.filter(category__type=type).all()
            else:
                queryset = cls.objects.filter(id__in=sample(range(1, count_db), count_for_section))
            for article in queryset:
                articles.append({
                    'title': article.title,
                    'views': article.views,
                    'img_url': article.image.url,
                    'url': reverse(f'{url_name}', kwargs={
                        'category_slug': article.category.slug,
                        'slug': article.slug,
                    }),
                    'url_section': reverse(f'{section}-categories'),
                })
            materials_by_sections[section] = articles

        return materials_by_sections


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
                ba.id,
                ba.title,
                ba.parent_id,
                ba.category_id,
                ba.slug
            FROM 
                knowledge_base_article ba

            JOIN knowledge_base_category bc ON bc.id = ba.category_id
            WHERE
                ba.parent_id IS NULL AND bc.type ='HNDBK'

            UNION
                SELECT 
                ba.id,
                ba.title,
                ba.parent_id,
                ba.category_id,
                ba.slug
            FROM 
                knowledge_base_article ba
            JOIN lessons t on ba.parent_id = t.id
            JOIN knowledge_base_category bc ON bc.id = ba.category_id
            WHERE bc.type ='HNDBK'
        ) SELECT 
                id, title,category_id as topic_id ,slug
            FROM
                lessons;
        """
        lessons_data = dict_fetch_all(sql)
        for lesson in lessons_data:
            topic__ordered_lessons_map[lesson['topic_id']].append(lesson)

        return topic__ordered_lessons_map


class Quiz(models.Model):
    title = models.TextField(verbose_name="Название")
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

    def __str__(self):
        return f'{self.category.title}:{self.title}'

    def get_absolute_url(self):
        return reverse('quiz', kwargs={'category_slug': self.category.slug, 'slug': self.slug})

    @classmethod
    def all_in_category(cls, slug):
        return cls.objects.filter(category__slug=slug).all()

    @classmethod
    def get_quiz_article_data(cls, slug: str):
        prefetch_questions = Prefetch('questions',
                                      queryset=Question.objects.prefetch_related('answers')
                                      .order_by('number'),
                                      to_attr='ordered_questions'
                                      )
        prefetch_results = Prefetch('results',
                                    queryset=QuizResult.objects.order_by('min_value'),
                                    to_attr='ordered_results'
                                    )
        article = cls.objects.prefetch_related(prefetch_questions, prefetch_results).get(slug=slug)

        quiz_article_data = {'title': article.title,
                             'img_url': article.image.url if article.image else None,
                             'time_for_read': article.time_for_read,
                             'views': article.views,
                             'questions': [],
                             'results': []}
        for question in article.ordered_questions:
            quiz_article_data['questions'].append(question.get_question_data())
        for result in article.ordered_results:
            quiz_article_data['results'].append(result.get_data())

        return quiz_article_data

    @classmethod
    def increase_views_by_one(cls, slug):
        obj = cls.objects.get(slug=slug)
        obj.views += 1
        obj.save()

    @classmethod
    def get_most_raited_materials(cls, count=4):
        articles = []

        count_db = cls.objects.aggregate(count=Count('id'))['count']
        if count > count_db:
            queryset = cls.objects.all()
        else:
            queryset = cls.objects.filter(id__in=sample(range(1, count_db), count))

        for article in queryset:
            articles.append({
                'title': article.title,
                'views': article.views,
                'img_url': article.image.url,
                'url': article.get_absolute_url(),
                'url_section': reverse(f'quizzes-categories'),
            })
        return articles


class Question(models.Model):
    number = models.PositiveIntegerField(validators=[MinValueValidator(1), ], verbose_name='номер вопроса')
    content = models.TextField(verbose_name='Содержание')
    quiz = models.ForeignKey(Quiz, verbose_name='Тест', on_delete=models.CASCADE, related_name='questions')

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = 'Вопросы'

    def __str__(self):
        return f'{self.quiz.title}: {self.number} - {self.content}'

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


class QuizResult(models.Model):
    min_value = models.IntegerField(validators=[MinValueValidator(0), ], verbose_name='нижняя граница результата')
    max_value = models.IntegerField(validators=[MinValueValidator(0), ], verbose_name='верхняя граница результата')
    content = models.TextField(verbose_name='Содержание')
    quiz = models.ForeignKey(Quiz, verbose_name='Тест', on_delete=models.CASCADE, related_name='results')

    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'

    def __str__(self):
        return f'{self.quiz.title}: {self.content}'

    def get_data(self):
        return {'content': self.content, 'min_value': self.min_value, 'max_value': self.max_value}
