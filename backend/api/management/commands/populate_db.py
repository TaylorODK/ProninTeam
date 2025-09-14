import random
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
import random
from faker import Faker
from api.models import Collect, Payment, Like, Comment

User = get_user_model()
fake = Faker()
stop_date = datetime.now() + timedelta(days=random.randint(1, 30))


class Command(BaseCommand):
    help = "Populate DB with mock data for Collect, Payment, Like, Comment"

    def add_arguments(self, parser):
        parser.add_argument(
            "--users", type=int, default=50, help="Number of users"
        )
        parser.add_argument(
            "--collects", type=int, default=20, help="Number of collects"
        )
        parser.add_argument(
            "--payments", type=int, default=200, help="Number of payments"
        )
        parser.add_argument(
            "--comments", type=int, default=500, help="Number of comments"
        )
        parser.add_argument(
            "--likes", type=int, default=500, help="Number of likes"
        )

    def handle(self, *args, **options):
        num_users = options["users"]
        num_collects = options["collects"]
        num_payments = options["payments"]
        num_comments = options["comments"]
        num_likes = options["likes"]

        users = []
        for _ in range(num_users):
            users.append(
                User(
                    username=fake.unique.user_name(),
                    email=fake.unique.email(),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                )
            )
        User.objects.bulk_create(users)
        users = list(User.objects.all())
        self.stdout.write(self.style.SUCCESS(f"{num_users} users created"))

        collects = []
        for _ in range(num_collects):
            min_payment = round(random.uniform(0, 100), 2)
            target_amount = round(random.uniform(min_payment + 1, 10000), 2)
            total_amount = round(random.uniform(target_amount + 1, 1000000), 2)
            author = random.choice(users)
            collects.append(
                Collect(
                    author=author,
                    name=fake.unique.sentence(nb_words=3),
                    slug=fake.unique.slug(),
                    description=fake.text(max_nb_chars=200),
                    event_format=random.choice(
                        [
                            choice[0]
                            for choice in Collect._meta.get_field(
                                "event_format"
                            ).choices
                        ]
                    ),
                    event_reason=random.choice(
                        [
                            choice[0]
                            for choice in Collect._meta.get_field(
                                "event_reason"
                            ).choices
                        ]
                    ),
                    event_date=fake.date_this_year(),
                    event_time=fake.time(),
                    event_place=fake.address(),
                    stop_date=stop_date,
                    min_payment=min_payment,
                    target_amount=target_amount,
                    total_amount=total_amount,
                )
            )
        Collect.objects.bulk_create(collects)
        collects = list(Collect.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f"{num_collects} collects created")
        )

        payments = []
        for _ in range(num_payments):
            payments.append(
                Payment(
                    author=random.choice(users),
                    collect=random.choice(collects),
                    amount=round(
                        random.uniform(min_payment, target_amount), 2
                    ),
                    hide_amount=random.choice([True, False]),
                )
            )
        Payment.objects.bulk_create(payments)
        payments = list(Payment.objects.all())
        self.stdout.write(
            self.style.SUCCESS(f"{num_payments} payments created")
        )

        comments = []
        for _ in range(num_comments):
            comments.append(
                Comment(
                    author=random.choice(users),
                    payment=random.choice(payments),
                    comment=fake.sentence(),
                )
            )
        Comment.objects.bulk_create(comments)
        self.stdout.write(
            self.style.SUCCESS(f"{num_comments} comments created")
        )

        likes = []
        seen = set()
        for _ in range(num_likes):
            user = random.choice(users)
            payment = random.choice(payments)
            if (user.id, payment.id) not in seen:
                likes.append(Like(author=user, payment=payment))
                seen.add((user.id, payment.id))
        Like.objects.bulk_create(likes)
        self.stdout.write(self.style.SUCCESS(f"{len(likes)} likes created"))
