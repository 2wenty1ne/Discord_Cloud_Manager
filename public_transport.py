import discord
from datetime import datetime, timedelta

#? Functions:
def create_final_public_transport_message(departure_time, departure_reason, shower_decision, walktime_min):
    walking_time_difference = timedelta(minutes=walktime_min)
    start_walking_time = departure_time - walking_time_difference

    if shower_decision:
        shower_time_difference =  timedelta(minutes=40)
        start_shower_time = start_walking_time - shower_time_difference
        geting_up_difference = timedelta(minutes=15)
        geting_up_time = start_shower_time - geting_up_difference
    else:
        geting_up_difference = timedelta(minutes=20)
        geting_up_time = start_walking_time - geting_up_difference

    first_alarm_difference = timedelta(minutes=20)
    first_alarm_time = geting_up_time - first_alarm_difference

    final_transport_message_embed = discord.Embed()
    final_transport_message_embed.color = discord.Color.from_rgb(255, 51, 153)

    final_transport_message_embed.title = f"{departure_reason} final plan"
    final_transport_message_embed_description = f'Your transport vehicle departs at: **{departure_time.strftime("%H:%M")}**\nYou should starting walking at: **{start_walking_time.strftime("%H:%M")}**\n'
    if shower_decision:
        final_transport_message_embed_description = final_transport_message_embed_description + f'You should start showering at: **{start_shower_time.strftime("%H:%M")}**\n'
    final_transport_message_embed_description = final_transport_message_embed_description + f'You should get up at **{geting_up_time.strftime("%H:%M")}**\nYour first alarm should go off at: **{first_alarm_time.strftime("%H:%M")}**'
    final_transport_message_embed.description = final_transport_message_embed_description
    return final_transport_message_embed


#? Classes:
class Public_transport_shower(discord.ui.Button):
    def __init__(self, color: str):
        super().__init__()

        self.color = color
        if self.color == "green":
            customstyle = discord.ButtonStyle.green
            customlabel = "YES"
            customid = "shower_green"
        else:
            customstyle = discord.ButtonStyle.red
            customlabel = "NO"
            customid = "shower_red"

        self.style = customstyle
        self.label = customlabel
        self.custom_id = customid

    async def callback(self, interaction: discord.Interaction):
        view: View = self.view

        if self.custom_id == "shower_green":
            view.change_shower_bool(True)
        elif self.custom_id == "shower_red":
            view.change_shower_bool(False)

        view.view_to_stops_decision()
        embed = discord.Embed()
        embed.color = discord.Color.from_rgb(45, 125 ,70)
        embed.title = "New public transport"
        embed.description = "Stop selection:"
        await interaction.response.edit_message(embed=embed, view=view)


class Public_transport_stops(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label='Kiosk', emoji='🟥', value="14"),
            discord.SelectOption(label='Church', emoji='🟩', value="10"),
            discord.SelectOption(label='Central station', emoji='🟪', value="20"),
            discord.SelectOption(label='Custom', emoji='🟦', value="Custom"),
        ]
        super().__init__(placeholder="Choose a stop", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        view: View = self.view

        if self.values[0] == "Custom":
            await interaction.response.send_modal(Public_transport_stop_input(self.view))
            return

        walktime_min = int(self.values[0])
        final_message_embed = self.view.view_to_final_message(walktime_min)
        await interaction.response.edit_message(embed=final_message_embed,view=self.view)


class Public_transport_stop_input(discord.ui.Modal, title="Custom stop"):
    def __init__(self, main_view):
        super().__init__()

        self.main_view = main_view

    user_input = discord.ui.TextInput(label="Input the walktime in minutes:")
    user_input.placeholder = "Walktime in minutes"
    user_input.required = True

    async def on_submit(self, interaction: discord.Interaction):
        if not self.user_input.value.isdigit():
            self.main_view.view_to_custom_stop_input_failure()

            custom_input_fail_embed = discord.Embed()
            custom_input_fail_embed.color = discord.Color.brand_red()
            custom_input_fail_embed.title = "Input failed"
            custom_input_fail_embed.description = f"Your input <{self.user_input.value}> needs to be a number! Try again."
            await interaction.response.edit_message(embed=custom_input_fail_embed, view=self.main_view)
            return

        walktime_min = int(self.user_input.value)
        final_message_embed = self.main_view.view_to_final_message(walktime_min)

        await interaction.response.edit_message(embed=final_message_embed,view=self.main_view)


class Public_transport_custom_fail(discord.ui.Button):
    def __init__(self):
        super().__init__()

        self.style = discord.ButtonStyle.red
        self.label = "Try again"

    async def callback(self, interaction :discord.Interaction):
        await interaction.response.send_modal(Public_transport_stop_input(self.view))


class Public_transportView(discord.ui.View):
    def __init__(self, departure_time, departure_reason):
        super().__init__(timeout=None)
        self.departure_time = departure_time
        self.departure_reason = departure_reason
        self.entire_walktime = 0
        self.shower_bool = False

        self.item_green = Public_transport_shower("green")
        self.add_item(self.item_green)

        self.item_red = Public_transport_shower("red")
        self.add_item(self.item_red)

        self.item_select = Public_transport_stops()
        self.custom_input_fail = Public_transport_custom_fail()


    def change_shower_bool(self, decision_bool):
        self.shower_bool = decision_bool

    def view_to_stops_decision(self):
        self.clear_items()
        self.add_item(self.item_select)

    def view_to_custom_stop_input_failure(self):
        self.clear_items()
        self.add_item(self.custom_input_fail)

    def view_to_final_message(self, walktime_min):
        self.clear_items()
        return create_final_public_transport_message(self.departure_time, self.departure_reason, self.shower_bool, walktime_min)