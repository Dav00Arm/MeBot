import utils
import file_operations
import webbrowser
import json

with open("data/projects.json", "r") as json_file:
    data = json.load(json_file)

# # Example chatbot flow
if __name__ == "__main__":
    if not file_operations.os.path.exists("data/chroma"):
        file_operations.embed_file("all_info.txt")
    print("Welcome! Ask me anything about Education, Projects, Certificates, or Experience.")
    while True:
        question = input("You: ")
        if question.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break
        response = utils.chatbot_response(question)
        if "link in a new tab" in response:
            project = utils.extract_project_name(response)
            try: 
                webbrowser.open(data[project]["Project"][0])
            except:
                response = f"Ohh... It seems {project} is private or unavailable. Sorry!"
        print(f"Bot: {response}")
        print("")
        
