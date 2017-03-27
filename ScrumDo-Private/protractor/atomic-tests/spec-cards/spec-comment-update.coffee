util = require("../util")

describe 'Scrumdo update Card comment' , ->

    afterEach () ->
        util.capture(jasmine.getEnv().currentSpec)

    
	
    it 'Should Archive all cards in a cell', ->
        browser.get param.projectUrl

        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(4).click().then ->
                element.all(By.css('button[ng-click="ctrl.ok()"]')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.css('.kanban-story-list li')).isPresent()).toBe false
        return
	
    cardName = param.cardName
    
    it 'Should add a card to cell', ->
        browser.get param.projectUrl
        element.all(By.css('.kanban-cell .scrumdo-column-title .scrumdo-column-dropdown')).get(0).element(By.tagName('button')).click().then ->
            element.all(By.css('.scrumdo-column-title')).get(0).all(By.css('.dropdown-menu li a')).get(0).click().then ->
                element(By.css('#summaryEditor div.scrumdo-mce-editor')).sendKeys(cardName).then ->
                   element.all(By.css('.nav-link')).get(1).click().then -> 
                    element.all(By.css('#ticketMessage')).get(0).sendKeys(param.storyComment).then ->
                        element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()
                        return
                    return
                return
            return
        browser.waitForAngular()
        expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return

    it 'Should update comment', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
           element.all(By.css('.nav-link')).get(2).click().then ->
            expect(element(By.css('.cards-log li')).isPresent()).toBe true
            element(By.css('span[ng-click="ctrl.makeEditable()"]')).click().then -> element(By.css('textarea[ng-model="ctrl.thisComment"]')).clear().then -> element.all(By.css('textarea[ng-model="ctrl.thisComment"]')).get(0).sendKeys(param.storyComment).then -> element(By.css('span[ng-click="ctrl.updateComment()"]')).click().then -> element(By.css('button[ng-click="ctrl.cancel()"]')).click().then -> 
            element.all(By.buttonText('Yes')).filter (elem) ->
                    return elem.isDisplayed()
                .click()
				
	
    it 'Should remove comment', ->
        element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then ->
           element.all(By.css('.nav-link')).get(2).click().then ->
            expect(element(By.css('.cards-log li')).isPresent()).toBe true
            element(By.css('span[ng-click="ctrl.deleteComment()"]')).click().then -> element(By.css('button[ng-click="ctrl.ok()"]')).click().then ->  
            element.all(By.css('button[ng-click="ctrl.save($event)"]')).filter (elem) ->
                            return elem.isDisplayed()
                        .click()