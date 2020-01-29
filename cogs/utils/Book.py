from datetime import datetime
import discord
import asyncio
import random

class BookList:
    def __init__(self):
        self.list = []
    def books(self):
        return self.list
    def add(self,obj):
        self.list.append(obj)
    def remove(self,obj):
        self.list.remove(obj)
class Book:
    class Page:
        def __init__(self,book=None,size=5,prevPage=None,nextPage=None):
            self.prevPage = prevPage
            if self.prevPage:
                self.book = self.prevPage.book
                self.number = self.prevPage.number+1
            else:
                self.book = book
                self.number = 1
            self.nextPage = nextPage
            self.content = []
            if self.book:
                self.size = self.book.pageSize
            else:
                self.size = size
 
        def add(self,item):
            self.content.append(item)
        def count(self):
            return len(self.content)
        def lenght(self):
            x = 0
            for i in self.content:
                x += len(i)
            return x
        
        def hightlight(self,idx):
            self.content[idx] = f'> {self.content[idx]} <'
       
    def __init__(self,booklist,author,name,content,pageSize):
        self.booklist = booklist
        
        for book in self.booklist.books():
            if book.author.id == author.id:
                book.close()
                break
        self.author = author
        self.message = None
        self.name = name
        self.pageSize = pageSize
        self.content = content
        self.stringizeContent()
        self.firstPage = Book.Page(book=self,size=self.pageSize)
        self.lastPage = self.firstPage
        self.currentPage = self.firstPage
        self.paginize()

        self.booklist.add(self)
    def paginize(self):
        page = self.firstPage
        for item in self.content:
            if page.lenght() + len(item) >= 2048 or page.count() == self.pageSize:
                nextPage = page.nextPage
                if nextPage:
                    page = nextPage
                else:
                    page.nextPage = Book.Page(self,self.pageSize,page)
                    page = page.nextPage
            page.add(item)



    def spacer(self,this,high):
        if high-this > 0:
            return " "*(high-this)
        return ""
    def stringizeContent(self):
        self.content.sort(key=lambda x: x.joined_at, reverse=False)

        temp = []
        i = 0
        for member in self.content:
            i+=1
            
            
            name = member.mention
            daysAgo = (datetime.now() - member.joined_at).days
            i_len = len(str(i))
            m_lem = len(str(len(self.content)))
            spaces = self.spacer(i_len,m_lem)
            guildDaysAgo = (datetime.now() - self.author.guild.created_at).days
            percent = int((daysAgo/guildDaysAgo)*100)

            if percent == 100:
                pref = '👑'
            elif percent >= 90:
                pref = '⭐'
            else:
                pref = '👤'
            name = f'{pref} {name}'
            text = f"`{i}{spaces}.` {name} [{percent}%] *Joined {daysAgo} days ago.*"
            temp.append(text)
        self.content = temp

    def pageCount(self):
        count = 0
        page = self.firstPage
        while page is not None:
            page = page.nextPage
            count += 1
        return count

    def preview(self):
        page = self.firstPage
        while page is not None:
            for item in page.content:
                print(item)
            page = page.nextPage
            print("\n\n")

    def goto(self,key):
        found = False
        page = self.firstPage
        while page:
            for i,item in enumerate(page.content):
                if key in item:
                    page.hightlight(i)
                    self.currentPage=page
                    found = True
                    break
            if found:
                break
            page = page.nextPage
        if not found:
            print('not found')
            self.currentPage = self.firstPage
    def nextPage(self):
        np = self.currentPage.nextPage
        if np:
            self.currentPage = np
            return True
        return False
    
    def prevPage(self):
        pp = self.currentPage.prevPage
        if pp:
            self.currentPage = pp
            return True
        return False
    def pageEmbed(self):
    
        embed = discord.Embed(description='\n'.join(self.currentPage.content),color=discord.Colour.from_rgb(random.randint(1,255),random.randint(1,255),random.randint(1,255)))
        
        if self.currentPage.book:
            title = f'{self.name} - Page {self.currentPage.number}/{self.pageCount()}'
        else:
            title = f'Page {self.currentPage.number}'
        embed.set_author(name=title)
           
        return embed
    def close(self):
        self.booklist.remove(self)
        del self

    async def handleReaction(self,reaction,user):
        if user.id != self.author.id or reaction.message.id != self.message.id:
            return
        if reaction.emoji == u"\U000023f9":
            self.close()
            return
        update = False
        if reaction.emoji == u"\U000025b6":
            
            update = self.nextPage()
        elif reaction.emoji == u"\U000025c0":    
            
            update = self.prevPage() 

        if update:
            await self.message.edit(embed=self.pageEmbed())