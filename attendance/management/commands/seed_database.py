import os
import django
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
from attendance.models import (
    Player, Game, CostRule, PlayerQuarterCostRule, Payment, OtherCharge,
    QuarterID, QuarterStartDatetime
)
import datetime
import random
from faker import Faker

fake = Faker()


class Command(BaseCommand):
    help = 'Seed the database with realistic fake data for UWH Attendance system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--players',
            type=int,
            default=25,
            help='Number of players to create'
        )
        parser.add_argument(
            '--games',
            type=int,
            default=100,
            help='Number of games to create'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            self.clear_data()

        self.stdout.write('Starting database seeding...')

        # Create cost rules first
        self.create_cost_rules()
        
        # Create players with users
        self.create_players(options['players'])
        
        # Create games
        self.create_games(options['games'])
        
        # Create player quarter cost rules
        self.create_player_quarter_cost_rules()
        
        # Create payments
        self.create_payments()
        
        # Create other charges
        self.create_other_charges()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully seeded database with:')
        )
        self.stdout.write(f'  - {User.objects.count()} users')
        self.stdout.write(f'  - {Player.objects.count()} players')
        self.stdout.write(f'  - {CostRule.objects.count()} cost rules')
        self.stdout.write(f'  - {Game.objects.count()} games')
        self.stdout.write(f'  - {PlayerQuarterCostRule.objects.count()} player quarter cost rules')
        self.stdout.write(f'  - {Payment.objects.count()} payments')
        self.stdout.write(f'  - {OtherCharge.objects.count()} other charges')

    def clear_data(self):
        """Clear all existing data"""
        OtherCharge.objects.all().delete()
        Payment.objects.all().delete()
        PlayerQuarterCostRule.objects.all().delete()
        Game.objects.all().delete()
        CostRule.objects.all().delete()
        Player.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

    def create_cost_rules(self):
        """Create cost rules for different quarters and player types"""
        self.stdout.write('Creating cost rules...')
        
        # Current quarter (approximate)
        current_quarter = QuarterID(timezone.now())
        
        # Create cost rules for last few quarters and future quarters
        for quarter_offset in range(-8, 4):  # 8 quarters back, 4 forward
            quarter = current_quarter + quarter_offset
            
            # Regular player rules
            cost_rules_data = [
                # Regular players
                {
                    'player_class': CostRule.REGULAR,
                    'is_visitor': False,
                    'quarterly_games_per_week': 0,
                    'game_cost': 8.00,
                    'quarter_cost': 0.00,
                    'covered_games_per_quarter': 0,
                    'free_games': 0,
                    'half_cost_games': 0,
                    'is_default': True,
                },
                {
                    'player_class': CostRule.REGULAR,
                    'is_visitor': False,
                    'quarterly_games_per_week': 1,
                    'game_cost': 8.00,
                    'quarter_cost': 75.00,
                    'covered_games_per_quarter': 12,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
                {
                    'player_class': CostRule.REGULAR,
                    'is_visitor': False,
                    'quarterly_games_per_week': 2,
                    'game_cost': 8.00,
                    'quarter_cost': 140.00,
                    'covered_games_per_quarter': 24,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
                {
                    'player_class': CostRule.REGULAR,
                    'is_visitor': False,
                    'quarterly_games_per_week': 3,
                    'game_cost': 8.00,
                    'quarter_cost': 200.00,
                    'covered_games_per_quarter': 36,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
                
                # Student players
                {
                    'player_class': CostRule.STUDENT,
                    'is_visitor': False,
                    'quarterly_games_per_week': 0,
                    'game_cost': 6.00,
                    'quarter_cost': 0.00,
                    'covered_games_per_quarter': 0,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
                {
                    'player_class': CostRule.STUDENT,
                    'is_visitor': False,
                    'quarterly_games_per_week': 1,
                    'game_cost': 6.00,
                    'quarter_cost': 55.00,
                    'covered_games_per_quarter': 12,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
                {
                    'player_class': CostRule.STUDENT,
                    'is_visitor': False,
                    'quarterly_games_per_week': 2,
                    'game_cost': 6.00,
                    'quarter_cost': 100.00,
                    'covered_games_per_quarter': 24,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
                
                # Junior players
                {
                    'player_class': CostRule.JUNIOR,
                    'is_visitor': False,
                    'quarterly_games_per_week': 0,
                    'game_cost': 4.00,
                    'quarter_cost': 0.00,
                    'covered_games_per_quarter': 0,
                    'free_games': 2,
                    'half_cost_games': 5,
                },
                {
                    'player_class': CostRule.JUNIOR,
                    'is_visitor': False,
                    'quarterly_games_per_week': 1,
                    'game_cost': 4.00,
                    'quarter_cost': 35.00,
                    'covered_games_per_quarter': 12,
                    'free_games': 2,
                    'half_cost_games': 5,
                },
                
                # Visitor rules
                {
                    'player_class': CostRule.REGULAR,
                    'is_visitor': True,
                    'quarterly_games_per_week': 0,
                    'game_cost': 12.00,
                    'quarter_cost': 0.00,
                    'covered_games_per_quarter': 0,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
                {
                    'player_class': CostRule.STUDENT,
                    'is_visitor': True,
                    'quarterly_games_per_week': 0,
                    'game_cost': 10.00,
                    'quarter_cost': 0.00,
                    'covered_games_per_quarter': 0,
                    'free_games': 0,
                    'half_cost_games': 0,
                },
            ]
            
            for rule_data in cost_rules_data:
                CostRule.objects.get_or_create(
                    player_class=rule_data['player_class'],
                    is_visitor=rule_data['is_visitor'],
                    quarterly_games_per_week=rule_data['quarterly_games_per_week'],
                    first_valid_quarter=quarter,
                    defaults=rule_data
                )

    def create_players(self, num_players):
        """Create players with associated users"""
        self.stdout.write(f'Creating {num_players} players...')
        
        for i in range(num_players):
            # Create user
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            # Ensure unique username
            counter = 1
            original_username = username
            while User.objects.filter(username=username).exists():
                username = f"{original_username}{counter}"
                counter += 1
                
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                first_name=first_name,
                last_name=last_name,
                password='defaultpassword123'
            )
            
            # Create player
            Player.objects.create(
                user=user,
                initial_num_games=random.randint(0, 50),
                initial_balance=round(random.uniform(-100, 200), 2),
                notes=fake.text(max_nb_chars=100) if random.random() < 0.3 else ''
            )

    def create_games(self, num_games):
        """Create games with random pools, times, and attendees"""
        self.stdout.write(f'Creating {num_games} games...')
        
        players = list(Player.objects.all())
        
        # Create games over the last 12 months
        end_date = timezone.now()
        start_date = end_date - datetime.timedelta(days=365)
        
        for i in range(num_games):
            # Random date/time within the range
            random_date = fake.date_time_between(start_date=start_date, end_date=end_date)
            random_date = timezone.make_aware(random_date)
            
            # Typical game times: Tuesday evenings, Saturday afternoons, Sunday mornings
            weekday = random_date.weekday()
            if weekday == 1:  # Tuesday
                start_time = random_date.replace(hour=19, minute=30, second=0, microsecond=0)
            elif weekday == 5:  # Saturday
                start_time = random_date.replace(hour=14, minute=0, second=0, microsecond=0)
            elif weekday == 6:  # Sunday
                start_time = random_date.replace(hour=10, minute=0, second=0, microsecond=0)
            else:
                # Random evening time for other days
                start_time = random_date.replace(
                    hour=random.randint(18, 20),
                    minute=random.choice([0, 30]),
                    second=0,
                    microsecond=0
                )
            
            # Game duration: 1.5 to 2.5 hours
            duration_minutes = random.randint(90, 150)
            end_time = start_time + datetime.timedelta(minutes=duration_minutes)
            
            # Pool selection based on day
            if weekday == 1:  # Tuesday - more likely Carmody
                pool = random.choices(
                    [Game.CARMODY, Game.VMAC, Game.EPIC],
                    weights=[60, 25, 15]
                )[0]
            elif weekday == 5:  # Saturday - more VMAC/EPIC
                pool = random.choices(
                    [Game.CARMODY, Game.VMAC, Game.EPIC],
                    weights=[20, 40, 40]
                )[0]
            else:
                pool = random.choices(
                    [Game.CARMODY, Game.VMAC, Game.EPIC],
                    weights=[40, 30, 30]
                )[0]
            
            game = Game.objects.create(
                pool=pool,
                starttime=start_time,
                endtime=end_time,
                shared_time_minutes=random.randint(0, 30) if random.random() < 0.2 else 0,
                notes=fake.sentence() if random.random() < 0.1 else ''
            )
            
            # Add random attendees (typically 8-20 players per game)
            num_attendees = random.randint(8, min(20, len(players)))
            attendees = random.sample(players, num_attendees)
            game.attendees.set(attendees)

    def create_player_quarter_cost_rules(self):
        """Create PlayerQuarterCostRules for players"""
        self.stdout.write('Creating player quarter cost rules...')
        
        current_quarter = QuarterID(timezone.now())
        players = Player.objects.all()
        
        for player in players:
            # Create rules for last 6 quarters and next 2 quarters
            for quarter_offset in range(-6, 3):
                quarter = current_quarter + quarter_offset
                
                # Determine cost rule based on player characteristics
                if random.random() < 0.1:  # 10% visitors
                    player_class = random.choice([CostRule.REGULAR, CostRule.STUDENT])
                    is_visitor = True
                    quarterly_games = 0
                elif random.random() < 0.15:  # 15% students
                    player_class = CostRule.STUDENT
                    is_visitor = False
                    quarterly_games = random.choice([0, 1, 2])
                elif random.random() < 0.05:  # 5% juniors
                    player_class = CostRule.JUNIOR
                    is_visitor = False
                    quarterly_games = random.choice([0, 1])
                else:  # Regular players
                    player_class = CostRule.REGULAR
                    is_visitor = False
                    quarterly_games = random.choice([0, 1, 1, 2, 2, 3])  # Weighted toward 1-2 games
                
                try:
                    cost_rule = CostRule.objects.filter(
                        player_class=player_class,
                        is_visitor=is_visitor,
                        quarterly_games_per_week=quarterly_games,
                        first_valid_quarter__lte=quarter
                    ).order_by('-first_valid_quarter').first()
                    
                    # Create PQCR using the model's GetOrCreate method
                    PlayerQuarterCostRule.GetOrCreate(
                        player=player,
                        quarter=quarter,
                        cost_rule=cost_rule
                    )
                    
                except (CostRule.DoesNotExist, AttributeError):
                    # Fall back to default rule
                    try:
                        default_rule = CostRule.objects.filter(
                            is_default=True,
                            first_valid_quarter__lte=quarter
                        ).order_by('-first_valid_quarter').first()
                        PlayerQuarterCostRule.GetOrCreate(
                            player=player,
                            quarter=quarter,
                            cost_rule=default_rule
                        )
                    except CostRule.DoesNotExist:
                        continue

    def create_payments(self):
        """Create payment records"""
        self.stdout.write('Creating payments...')
        
        players = Player.objects.all()
        current_date = timezone.now()
        start_date = current_date - datetime.timedelta(days=365)
        
        # Each player makes 2-6 payments over the year
        for player in players:
            num_payments = random.randint(2, 6)
            
            for _ in range(num_payments):
                payment_date = fake.date_time_between(start_date=start_date, end_date=current_date)
                payment_date = timezone.make_aware(payment_date)
                
                # Payment types with realistic weights
                payment_type = random.choices(
                    [Payment.CHECK, Payment.PAYPAL, Payment.CASH, Payment.DIRECT_DEPOSIT, Payment.ACCOUNT_CREDIT],
                    weights=[30, 25, 20, 15, 10]
                )[0]
                
                # Payment amounts typically in increments of $5, $25, or quarterly amounts
                amount_options = [25, 50, 75, 100, 125, 150, 175, 200, 225, 250]
                amount = random.choice(amount_options)
                
                # Generate reference based on payment type
                if payment_type == Payment.CHECK:
                    reference = f"Check #{random.randint(1000, 9999)}"
                elif payment_type == Payment.PAYPAL:
                    reference = f"PayPal transaction {fake.uuid4()[:8]}"
                elif payment_type == Payment.DIRECT_DEPOSIT:
                    reference = f"Direct deposit {fake.date()}"
                elif payment_type == Payment.ACCOUNT_CREDIT:
                    reference = "Account credit adjustment"
                else:
                    reference = ""
                
                Payment.objects.create(
                    player=player,
                    time=payment_date,
                    amount=amount,
                    payment_type=payment_type,
                    reference=reference
                )

    def create_other_charges(self):
        """Create other charge records"""
        self.stdout.write('Creating other charges...')
        
        players = Player.objects.all()
        current_date = timezone.now()
        start_date = current_date - datetime.timedelta(days=365)
        
        # Some players (about 30%) have additional charges
        selected_players = random.sample(list(players), int(len(players) * 0.3))
        
        charge_types = [
            ("Equipment rental", 10.00),
            ("Locker fee", 5.00),
            ("Tournament entry", 25.00),
            ("Late payment fee", 15.00),
            ("Equipment replacement", 45.00),
            ("Guest pass", 12.00),
            ("Training clinic", 30.00),
            ("Membership processing", 5.00),
        ]
        
        for player in selected_players:
            # 1-3 charges per selected player
            num_charges = random.randint(1, 3)
            
            for _ in range(num_charges):
                charge_date = fake.date_time_between(start_date=start_date, end_date=current_date)
                charge_date = timezone.make_aware(charge_date)
                
                charge_type, base_amount = random.choice(charge_types)
                # Add some variation to the amount
                amount = base_amount + random.uniform(-5, 15)
                amount = round(amount, 2)
                
                OtherCharge.objects.create(
                    player=player,
                    time=charge_date,
                    amount=amount,
                    remarks=charge_type
                )

    def create_number_file(self):
        """Create the 'number' file that some legacy functions expect"""
        try:
            with open('number', 'w') as f:
                f.write('1000')
        except Exception as e:
            self.stdout.write(f'Could not create number file: {e}')
