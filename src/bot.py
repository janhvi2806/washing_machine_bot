import discord
from discord.ext import commands
import asyncio
import logging
from typing import Optional

from config import Config
from llm_handler import LLMHandler
from mantis_client import MantisHubClient
from database import DatabaseHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=Config.COMMAND_PREFIX, intents=intents)

# Initializing components
db = DatabaseHandler(Config.DATABASE_PATH)
llm_handler = LLMHandler()
mantis_client = MantisHubClient()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    print(f'Bot is ready to help with washing machine support!')

@bot.event
async def on_message(message):
    # Ignore bot messages
    if message.author == bot.user:
        return
    
    # Only respond in support channel or DMs
    if Config.SUPPORT_CHANNEL_ID and message.channel.id != Config.SUPPORT_CHANNEL_ID and not isinstance(message.channel, discord.DMChannel):
        return
    
    # Skip if message starts with command prefix
    if message.content.startswith(Config.COMMAND_PREFIX):
        await bot.process_commands(message)
        return
    
    # Process the message
    await handle_support_message(message)

async def handle_support_message(message):
    """Handle support-related messages"""
    user_id = str(message.author.id)
    user_message = message.content.strip()
    
    try:
        async with message.channel.typing():
            # Get conversation history - FIX THE ERROR HERE
            conversation_history = db.get_session(user_id)
            if conversation_history is None:
                conversation_history = {'messages': []}
            
            # Process with LLM
            llm_response = await llm_handler.process_query(user_message, conversation_history.get('messages', []))
            
            # Update conversation history
            if 'messages' not in conversation_history:
                conversation_history['messages'] = []
            
            conversation_history['messages'].append({"role": "user", "content": user_message})
            conversation_history['messages'].append({"role": "assistant", "content": llm_response['response']})
            
            # Handle different actions
            if llm_response['action'] == 'create_ticket':
                await handle_ticket_creation(message, llm_response, user_id)
            elif llm_response['action'] == 'troubleshoot':
                await send_troubleshooting_response(message, llm_response)
            else:
                await send_clarification_response(message, llm_response)
            
            db.update_session(user_id, conversation_history)
            
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        await message.reply("I'm sorry, I encountered an error. Please try again later.")

async def handle_ticket_creation(message, llm_response, user_id):
    """Handle ticket creation process"""
    
    # Create ticket in Mantis Hub
    ticket_id = mantis_client.create_ticket(
        summary=llm_response.get('ticket_summary', 'Washing Machine Issue'),
        description=f"Issue reported by Discord user {message.author.display_name}:\n\n{message.content}",
        reporter_name=message.author.display_name,
        category=llm_response.get('category', 'General'),
        priority=llm_response.get('priority', 40)
    )
    
    if ticket_id:
        # Save to database
        db.create_ticket_record(user_id, ticket_id, llm_response.get('ticket_summary', 'Washing Machine Issue'))
        
        # Create embed for ticket confirmation
        embed = discord.Embed(
            title="🎫 Support Ticket Created",
            description=llm_response['response'],
            color=0x00ff00
        )
        embed.add_field(name="Ticket Number", value=f"#{ticket_id}", inline=True)
        embed.add_field(name="Status", value="New", inline=True)
        embed.add_field(name="Category", value=llm_response.get('category', 'General'), inline=True)
        embed.set_footer(text="You can reference this ticket number for future updates.")
        
        await message.reply(embed=embed)
    else:
        await message.reply("I apologize, but I couldn't create a support ticket at the moment. Please try again later or contact support directly.")

async def send_troubleshooting_response(message, llm_response):
    """Send troubleshooting response to user"""
    
    embed = discord.Embed(
        title="🔧 Troubleshooting Steps",
        description=llm_response['response'],
        color=0x0099ff
    )
    embed.set_footer(text="If these steps don't help, let me know and I can create a support ticket for you.")
    
    await message.reply(embed=embed)

async def send_clarification_response(message, llm_response):
    """Send clarification response to user"""
    
    embed = discord.Embed(
        title="🤖 Support Assistant",
        description=llm_response['response'],
        color=0xffaa00
    )
    
    await message.reply(embed=embed)

# Commands
@bot.command(name='tickets')
async def show_tickets(ctx):
    """Show user's tickets"""
    user_id = str(ctx.author.id)
    tickets = db.get_user_tickets(user_id)
    
    if not tickets:
        await ctx.reply("You don't have any support tickets.")
        return
    
    embed = discord.Embed(
        title="📋 Your Support Tickets",
        color=0x0099ff
    )
    
    for ticket in tickets[:5]:
        ticket_id, summary, created_at, status = ticket
        embed.add_field(
            name=f"Ticket #{ticket_id}",
            value=f"**{summary}**\nCreated: {created_at}\nStatus: {status}",
            inline=False
        )
    
    await ctx.reply(embed=embed)

@bot.command(name='status')
async def check_ticket_status(ctx, ticket_id: str):
    """Check status of a specific ticket"""
    
    ticket_info = mantis_client.get_ticket_status(ticket_id)
    
    if ticket_info:
        issue = ticket_info.get('issues', [{}])[0]
        
        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_id} Status",
            color=0x00ff00
        )
        embed.add_field(name="Summary", value=issue.get('summary', 'N/A'), inline=False)
        embed.add_field(name="Status", value=issue.get('status', {}).get('name', 'Unknown'), inline=True)
        embed.add_field(name="Priority", value=issue.get('priority', {}).get('name', 'Unknown'), inline=True)
        embed.add_field(name="Assigned To", value=issue.get('handler', {}).get('name', 'Unassigned'), inline=True)
        
        await ctx.reply(embed=embed)
    else:
        await ctx.reply(f"Could not find ticket #{ticket_id} or you don't have permission to view it.")

@bot.command(name='help_washing')
async def help_command(ctx):
    """Show help information"""
    
    embed = discord.Embed(
        title="🧺 Washing Machine Support Bot",
        description="I'm here to help you with washing machine issues!",
        color=0x0099ff
    )
    
    embed.add_field(
        name="How to get help:",
        value="Simply describe your washing machine problem in natural language.",
        inline=False
    )
    
    embed.add_field(
        name="Available Commands:",
        value="""
        `!tickets` - View your support tickets
        `!status <ticket_id>` - Check ticket status
        `!help_washing` - Show this help message
        """,
        inline=False
    )
    
    embed.add_field(
        name="Example Questions:",
        value="""
        • "My washing machine won't drain"
        • "The detergent isn't dispensing properly"
        • "There's excessive noise during spin cycle"
        • "My clothes aren't getting clean"
        """,
        inline=False
    )
    
    await ctx.reply(embed=embed)

# Error handling
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    
    logger.error(f"Command error: {error}")
    await ctx.reply("An error occurred while processing your command.")

if __name__ == "__main__":
    bot.run(Config.DISCORD_TOKEN)
