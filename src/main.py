import os
from datetime import datetime

from discord_webhook import DiscordWebhook, DiscordEmbed
from plexapi.server import PlexServer
from dotenv import load_dotenv
import requests
from io import BytesIO

load_dotenv()

WEBHOOK_URL = os.environ["WEBHOOK_URL"]
PLEX_URL = os.environ["PLEX_URL"]
PLEX_TOKEN = os.environ["PLEX_TOKEN"]
FILENAME = "last_execution.txt"

def main():
    # plex
    plex = PlexServer(PLEX_URL, PLEX_TOKEN)

    # discord
    webhook = DiscordWebhook(url=WEBHOOK_URL)

    # read or create last update file
    try:
        with open(FILENAME, "r") as file:
            last_execution = int(file.readline())
    except FileNotFoundError:
        last_execution = None

    # get recently added videos
    movies = plex.library.recentlyAdded()
    for (index, movie) in enumerate(movies):
        added_at = int(movie.addedAt.timestamp())

        # if movie is older than last added date, skip it
        if last_execution is None or added_at < last_execution:
            break

        embed = DiscordEmbed(
            title=movie.title,
            description=movie.summary,
            color=movie.ultraBlurColors.topLeft if movie.ultraBlurColors else "EBAF00"
        )

        if movie.year:
            embed.add_embed_field(name="Année de sortie", value=str(movie.year))

        if movie.audienceRating:
            embed.add_embed_field(name="Note des spectateurs", value=f"{movie.audienceRating} / 10")

        if hasattr(movie, "genres") and movie.genres:
            embed.add_embed_field(name="Genres" if len(movie.genres) > 1 else "Genre", value=", ".join([genre.tag for genre in movie.genres]))

        if hasattr(movie, "roles") and movie.roles:
            embed.add_embed_field(name="Acteurs" if len(movie.roles) > 1 else "Acteur", value=", ".join([role.tag for role in movie.roles]))

        if hasattr(movie, "directors") and movie.directors:
            embed.add_embed_field(name="Réalisateurs" if len(movie.directors) > 1 else "Réalisateur", value=", ".join([director.tag for director in movie.directors]))

        webhook.add_embed(embed)

        webhook.content=f"Nouveau film ajouté sur Plex : https://app.plex.tv/desktop/#!/server/{plex.machineIdentifier}/details?key={movie.key}"

        # thumbnail
        if movie.thumbUrl:
            response = requests.get(movie.thumbUrl)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                webhook.add_file(file=image_data, filename="thumb.jpg")
                embed.set_thumbnail(url="attachment://thumb.jpg")

        # send Discord message
        webhook.execute()

    # write last execution date
    with open(FILENAME, "w") as file:
        timestamp = int(datetime.now().timestamp())
        file.write(str(timestamp))

if __name__ == "__main__":
    main()
