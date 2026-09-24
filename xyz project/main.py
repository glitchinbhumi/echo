from database import (
    initialize_database,
    save_memory,
    search_memories,
    get_memories
)

from conversation import (
    get_relevant_memories,
    ask_groq
)


# ==========================================
# INITIALIZE ECHO
# ==========================================

initialize_database()


# ==========================================
# DISPLAY HEADER
# ==========================================

def show_header():

    print("\n")
    print("╔══════════════════════════════════════════╗")
    print("║                  ECHO                    ║")
    print("║       A memory that outlives you.        ║")
    print("╚══════════════════════════════════════════╝")


# ==========================================
# ADD A MEMORY
# ==========================================

def add_memory():

    print("\n")
    print("========================================")
    print("          PRESERVE A MEMORY")
    print("========================================")

    person = input("\nWho is this memory about? ")

    text = input("\nTell me the memory: ")

    year = input("\nWhat year did this happen? ")

    if year.strip() == "":
        year = None
    else:
        try:
            year = int(year)
        except ValueError:
            print("\nInvalid year. Leaving year empty.")
            year = None

    place = input("\nWhere did this happen? ")

    importance = input(
        "\nHow important is this memory (0-1)? "
    )

    try:
        importance = float(importance)

    except ValueError:
        importance = 0.5
        print("Invalid importance. Using 0.5.")


    memory = {
        "person": person,
        "text": text,
        "year": year,
        "place": place,
        "importance": importance
    }


    save_memory(memory)

    print("\n🧠 Memory successfully preserved in ECHO.")


# ==========================================
# SEARCH MEMORIES
# ==========================================

def explore_memories():

    print("\n")
    print("========================================")
    print("           EXPLORE MEMORIES")
    print("========================================")

    keyword = input("\nWhat do you want to remember? ")

    results = search_memories(keyword)


    if not results:

        print("\nECHO couldn't find a matching memory.")

        return


    print("\n--- Memories Found ---")


    for memory in results:

        print("\n----------------------------------------")

        print("Memory ID:", memory[0])
        print("Person:", memory[1])
        print("Memory:", memory[2])
        print("Year:", memory[3])
        print("Place:", memory[4])
        print("Importance:", memory[5])


# ==========================================
# TALK TO ECHO
# ==========================================

def talk_to_echo():

    print("\n")
    print("========================================")
    print("             TALK TO ECHO")
    print("========================================")

    print("\nType 'exit' to leave the conversation.")


    while True:

        question = input("\nYou: ")


        if question.lower().strip() == "exit":

            print("\nLeaving ECHO conversation...")

            break


        print("\n🔎 Searching preserved memories...")


        memory_context = get_relevant_memories(question)


        print("🧠 Memories retrieved.")

        print("🤖 ECHO is thinking...")


        try:

            answer = ask_groq(
                memory_context,
                question
            )

            print("\nECHO:")
            print(answer)


        except Exception as error:

            print("\n❌ Something went wrong.")
            print("Error:", error)


# ==========================================
# MEMORY TIMELINE
# ==========================================

def memory_timeline():

    print("\n")
    print("========================================")
    print("           MEMORY TIMELINE")
    print("========================================")


    memories = get_memories()


    if not memories:

        print("\nNo memories have been preserved yet.")

        return


    # Sort memories by year
    memories = sorted(
        memories,
        key=lambda memory: (
            memory[3] is None,
            memory[3] if memory[3] is not None else 0
        )
    )


    for memory in memories:

        print("\n----------------------------------------")

        if memory[3] is not None:

            print("📅", memory[3])

        else:

            print("📅 Year unknown")


        print("👤", memory[1])

        print("📍", memory[4])

        print("💭", memory[2])


# ==========================================
# MAIN MENU
# ==========================================

def main():

    while True:

        show_header()


        print("\nWhat would you like to do?\n")

        print("1. 📝 Preserve a Memory")
        print("2. 🔎 Explore Memories")
        print("3. 💬 Talk to ECHO")
        print("4. 📜 View Memory Timeline")
        print("5. 🚪 Exit")


        choice = input("\nChoose an option: ")


        if choice == "1":

            add_memory()


        elif choice == "2":

            explore_memories()


        elif choice == "3":

            talk_to_echo()


        elif choice == "4":

            memory_timeline()


        elif choice == "5":

            print("\nECHO is closing...")

            print("Your memories remain preserved. 🧠")

            break


        else:

            print("\n❌ Invalid choice. Please choose 1-5.")


# ==========================================
# START ECHO
# ==========================================

if __name__ == "__main__":

    main()