from tft import Team
from tftui import TraitTracker
import asyncio


async def testrun():
    team = Team.from_names(["Ahri", "Rakan", "Rumble"])
    async for solution in team.find_champs_rust():
        for trait in solution.traits:
            print(trait.trait_.name)
        # print(solution.traits)


if __name__ == "__main__":
    TraitTracker().run()
    # asyncio.run(testrun())
