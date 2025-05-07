from app_with_memory import Shoppingass
from states import State
import traceback
while True :
    try:
        user_input=input("Enter:")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Bye")
            break
        s = State(session_id="user123",msg=[user_input],input_type="text")
        
        g = Shoppingass()
        result=g.graph.invoke(s)
        print(result)
        # agent.stream_graph_updates(user_input)
    except Exception as e:
        print("Error:", e)
        traceback.print_exc()
        break