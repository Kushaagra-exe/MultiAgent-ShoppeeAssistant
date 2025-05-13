from app_with_memory import Shoppingass
from states import State, VlmResponse
import traceback
while True :
    try:
        user_input=input("Enter:")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Bye")
            break
        s = State(session_id="user123",msg=[user_input],input_type="text")
        product_info = VlmResponse(description={'product': 'fabric', 'brand': None, 'style': 'Paisley', 'quality': 'Medium', 'color': 'Yellow and Green', 'pattern': 'Striped and Floral', 'material': 'Cotton'},
                                   product_details={
 "product": "Yellow and Green Paisley Pattern Fabric",
 "category": "Textiles - Fabrics",
 "detailed_explanation": "This fabric features a vibrant yellow base with a distinctive paisley pattern in green. The paisley designs are intricate and repeated across the lower portion of the fabric, while the upper part showcases horizontal green stripes. The fabric appears to have a soft, possibly cotton or cotton-blend texture, suitable for clothing, home decor, or crafting projects.",
 "common_uses": ["Clothing (dresses, scarves, shirts)", "Home decor (curtains, pillow covers)", "Crafting (quilting, sewing projects)"],
 "who_might_use_this": ["Fashion designers", "Interior decorators", "Crafters", "Sewing enthusiasts"],
 "related_products_or_alternatives": ["Solid color fabrics", "Other patterned fabrics (floral, geometric)", "Cotton or linen fabrics with similar textures"]
}
        )
        # product_info = VlmResponse(description={'product_name': 'Nike Graphic T-Shirt', 'category': 'Fashion - Apparel', 'detailed_explanation': "This is a black, short-sleeved T-shirt made by Nike, a well-known sports apparel brand. The shirt features a large graphic print on the front, which includes the Nike logo (a white checkmark) and the word 'NIKE' in white text, set against a colorful background of tropical flowers and leaves. The T-shirt is made of comfortable, breathable material, likely cotton or a cotton-blend fabric, and has a casual fit. The design is typical of Nike's fashion-forward approach to sportswear, making it suitable for both athletic and everyday wear.", 'common_uses': ['Casual wear', 'Athleisure', 'Running', 'Gym workouts', 'Lounging'], 'who_might_use_this': ['Young adults', 'Fitness enthusiasts', 'Fashion-conscious consumers', 'Athletes', 'Anyone looking for comfortable, stylish casual wear'], 'related_products_or_alternatives': ['Adidas graphic T-shirts', 'Under Armour sportswear', 'Champion T-shirts', 'Hanes comfortable tees']},
        #                            product_details={'product': 't-shirt', 'brand': 'Nike', 'style': 'Graphic T-shirt', 'quality': 'Medium-High', 'features': ['Crew Neck', 'Short Sleeves', 'Tropical Print', 'Logo Branding']}
        # )
        s = State(session_id="user1234",msg=[user_input],input_type="text", product_info=product_info)
        
        g = Shoppingass()
        result=g.graph.invoke(s)
        print(result)
        # agent.stream_graph_updates(user_input)
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        break