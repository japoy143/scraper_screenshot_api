from utils.scraper import run_actions

web_link = "https://rainierlesondatoii.vercel.app/"

sample_actions = [
    {
        "action": "get_by_role",
        "role": "link",
        "name": "Contact",
        "secondary_action": "click",
        "input": "",
    },
    {
        "action": "screenshot",
        "role": "",
        "name": "",
        "secondary_action": "",
        "input": "",
    },
]

content = run_actions(web_link, sample_actions)
print(content)
