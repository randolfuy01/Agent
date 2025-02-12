from agent import Chat_Agent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initial_set_up():

    logger.info("Begin unit testing for inference")

    # Initialization
    try:
        logger.info("Instantiating chat agent")
        agent = Chat_Agent(index_name="personal")
        agent.instantiate_api()
    except Exception as e:
        logger.error(f"Error during API instantiation: {e}")

    query_testing = [
        "Can you tell me more about his internship experience?",
        "Can you go into detail about his education?",
        "Do you think he would fit well into a devOps engineering role or a backend engineering role?",
        "Besides work, what kind of hobbies is Randolf into? You know like hobbies?",
    ]

    counter = 0

    # inference
    logger.info("Starting inference")
    try:
        for query in query_testing:
            validation = unit_test(agent, query)
            logger.info(f"Question {counter}: {query}")
            logger.info(f"Response {counter}: {validation}")
            counter += 1

    except Exception as e:
        logger.error(f"Error during inference {counter}: {e}")


def unit_test(agent: Chat_Agent, query: str) -> str:
    try:
        response = agent.response(query)
    except Exception as e:
        logger.error(f"Error during chatbot response generation: {e}")

    return response.choices[0].message.content


def main():
    initial_set_up()


if __name__ == "__main__":
    main()
