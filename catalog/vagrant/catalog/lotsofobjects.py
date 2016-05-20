from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from catalog_setup import Catagory, Base, Object, User

engine = create_engine('sqlite:///catalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com", picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Menu for UrbanBurger
catagory1 = Catagory(user_id=1, name="Soccer")

session.add(catagory1)
session.commit()

object2 = Object(user_id=1, name="Shingaurds", description="For protecting your shins",
       catagory=catagory1)

session.add(object2)
session.commit()


object1 = Object(user_id=1, name="Jersey", description="Shirt that shows your team number",
       catagory=catagory1)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Cleats", description="For better mobility one the field",
       catagory=catagory1)

session.add(object2)
session.commit()

object3 = Object(user_id=1, name="Chocolate Cake", description="fresh baked and served with ice cream",
       catagory=catagory1)

session.add(object3)
session.commit()

# Menu for Super Stir Fry
catagory2 = Catagory(user_id=1, name="Baseball")

session.add(catagory2)
session.commit()


object1 = Object(user_id=1, name="Bat", description="For hitting the baseball",
       catagory=catagory2)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Base",
                     description="For running to in order to score runs",
                     catagory=catagory2)

session.add(object2)
session.commit()

#Menu for Panda Garden
catagory3 = Catagory(user_id=1, name="Snowboarding")

session.add(catagory3)
session.commit()


object1 = Object(user_id=1, name="Snowboard", description="For riding on",
       catagory=catagory3)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Googles", description="Helps you see through the snow at high speeds",
                     catagory=catagory3)

'''
# Menu for Thyme for that
catagory4 = Catagory(user_id=1, name="Thyme for That Vegetarian Cuisine ")

session.add(catagory4)
session.commit()


object1 = Object(user_id=1, name="Tres Leches Cake", description="Rich, luscious sponge cake soaked in sweet milk and topped with vanilla bean whipped cream and strawberries.",
                     catagory=catagory4)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Mushroom risotto", description="Portabello mushrooms in a creamy risotto",
                     catagory=catagory4)

session.add(object2)
session.commit()

object3 = Object(user_id=1, name="Honey Boba Shaved Snow",
                     description="Milk snow layered with honey boba, jasmine tea jelly, grass jelly, caramel, cream, and freshly made mochi",
                     catagory=catagory4)

session.add(object3)
session.commit()

object4 = Object(user_id=1, name="Cauliflower Manchurian", description="Golden fried cauliflower florets in a midly spiced soya,garlic sauce cooked with fresh cilantro, celery, chilies,ginger & green onions",
                     catagory=catagory4)

session.add(object4)
session.commit()

object5 = Object(user_id=1, name="Aloo Gobi Burrito", description="Vegan goodness. Burrito filled with rice, garbanzo beans, curry sauce, potatoes (aloo), fried cauliflower (gobi) and chutney. Nom Nom",
                     catagory=catagory4)

session.add(object5)
session.commit()

object6 = Object(user_id=1, name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                     catagory=catagory4)

session.add(object6)
session.commit()


# Menu for Tony's Bistro
catagory5 = Catagory(user_id=1, name="Tony\'s Bistro ")

session.add(catagory5)
session.commit()


object1 = Object(user_id=1, name="Shellfish Tower", description="Lobster, shrimp, sea snails, crawfish, stacked into a delicious tower",
                     catagory=catagory5)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Chicken and Rice", description="Chicken... and rice",
                     catagory=catagory5)

session.add(object2)
session.commit()

object3 = Object(user_id=1, name="Mom's Spaghetti", description="Spaghetti with some incredible tomato sauce made by mom",
                     catagory=catagory5)

session.add(object3)
session.commit()


object4 = Object(user_id=1, name="Choc Full O\' Mint (Smitten\'s Fresh Mint Chip ice cream)",
                     description="Milk, cream, salt, ..., Liquid nitrogen magic", price="$3.95", course="Dessert", catagory=catagory1)

session.add(object4)
session.commit()

object5 = Object(user_id=1, name="Tonkatsu Ramen", description="Noodles in a delicious pork-based broth with a soft-boiled egg",
                     price="$7.95", course="Entree", catagory=catagory1)

session.add(object5)
session.commit()


# Menu for Andala's
catagory1 = Catagory(user_id=1, name="Andala\'s")

session.add(catagory1)
session.commit()


object1 = Object(user_id=1, name="Lamb Curry", description="Slow cook that thang in a pool of tomatoes, onions and alllll those tasty Indian spices. Mmmm.",
                     price="$9.95", course="Entree", catagory=catagory1)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Chicken Marsala", description="Chicken cooked in Marsala wine sauce with mushrooms",
                     price="$7.95", course="Entree", catagory=catagory1)

session.add(object2)
session.commit()

object3 = Object(user_id=1, name="Potstickers", description="Delicious chicken and veggies encapsulated in fried dough.",
                     price="$6.50", course="Appetizer", catagory=catagory1)

session.add(object3)
session.commit()

object4 = Object(user_id=1, name="Nigiri Sampler", description="Maguro, Sake, Hamachi, Unagi, Uni, TORO!",
                     price="$6.75", course="Appetizer", catagory=catagory1)

session.add(object4)
session.commit()

object2 = Object(user_id=1, name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                     price="$7.00", course="Entree", catagory=catagory1)

session.add(object2)
session.commit()


# Menu for Auntie Ann's
catagory1 = Catagory(user_id=1, name="Auntie Ann\'s Diner' ")

session.add(catagory1)
session.commit()

object9 = Object(user_id=1, name="Chicken Fried Steak",
                     description="Fresh battered sirloin steak fried and smothered with cream gravy", price="$8.99", course="Entree", catagory=catagory1)

session.add(object9)
session.commit()


object1 = Object(user_id=1, name="Boysenberry Sorbet", description="An unsettlingly huge amount of ripe berries turned into frozen (and seedless) awesomeness",
                     price="$2.99", course="Dessert", catagory=catagory1)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Broiled salmon", description="Salmon fillet marinated with fresh herbs and broiled hot & fast",
                     price="$10.95", course="Entree", catagory=catagory1)

session.add(object2)
session.commit()

object3 = Object(user_id=1, name="Morels on toast (seasonal)",
                     description="Wild morel mushrooms fried in butter, served on herbed toast slices", price="$7.50", course="Appetizer", catagory=catagory1)

session.add(object3)
session.commit()

object4 = Object(user_id=1, name="Tandoori Chicken", description="Chicken marinated in yoghurt and seasoned with a spicy mix(chilli, tamarind among others) and slow cooked in a cylindrical clay or metal oven which gets its heat from burning charcoal.",
                     price="$8.95", course="Entree", catagory=catagory1)

session.add(object4)
session.commit()

object2 = Object(user_id=1, name="Veggie Burger", description="Juicy grilled veggie patty with tomato mayo and lettuce",
                     price="$9.50", course="Entree", catagory=catagory1)

session.add(object2)
session.commit()

object10 = Object(user_id=1, name="Spinach Ice Cream", description="vanilla ice cream made with organic spinach leaves",
                      price="$1.99", course="Dessert", catagory=catagory1)

session.add(object10)
session.commit()


# Menu for Cocina Y Amor
catagory1 = Catagory(user_id=1, name="Cocina Y Amor ")

session.add(catagory1)
session.commit()


object1 = Object(user_id=1, name="Super Burrito Al Pastor",
                     description="Marinated Pork, Rice, Beans, Avocado, Cilantro, Salsa, Tortilla", price="$5.95", course="Entree", catagory=catagory1)

session.add(object1)
session.commit()

object2 = Object(user_id=1, name="Cachapa", description="Golden brown, corn-based Venezuelan pancake; usually stuffed with queso telita or queso de mano, and possibly lechon. ",
                     price="$7.99", course="Entree", catagory=catagory1)

session.add(object2)
session.commit()


catagory1 = Catagory(user_id=1, name="State Bird Provisions")
session.add(catagory1)
session.commit()

object1 = Object(user_id=1, name="Chantrelle Toast", description="Crispy Toast with Sesame Seeds slathered with buttery chantrelle mushrooms",
                     price="$5.95", course="Appetizer", catagory=catagory1)

session.add(object1)
session.commit

object1 = Object(user_id=1, name="Guanciale Chawanmushi",
                     description="Japanese egg custard served hot with spicey Italian Pork Jowl (guanciale)", price="$6.95", course="Dessert", catagory=catagory1)

session.add(object1)
session.commit()


object1 = Object(user_id=1, name="Lemon Curd Ice Cream Sandwich",
                     description="Lemon Curd Ice Cream Sandwich on a chocolate macaron with cardamom meringue and cashews", price="$4.25", course="Dessert", catagory=catagory1)

session.add(object1)
session.commit()
'''

print "added menu items!"