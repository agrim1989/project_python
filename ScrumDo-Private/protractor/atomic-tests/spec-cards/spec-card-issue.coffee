util = require("../util")

describe 'Scrumdo issue filter card' , ->

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
		
    it 'Should issue changed to processing', ->
	       browser.get param.projectUrl
		
	       element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(0).all(By.css('li.cards div.cards-header span.pull-right')).last().click().then -> browser.sleep(2000).then ->
            element(By.css('.scrumdo-btn.primary.extended.scrumdo-select-button.scrumdo-fixed-size')).click().then -> browser.sleep(2000).then ->
			             element.all(By.css('.dropdown-menu  sd-cell-picker .cell-picker .picker-content sd-board-preview svg g g')).get(1).all(By.css('g[id="cell_216185"] rect')).get(0).click().then ->
                    element(By.xpath('//button[@ng-click="ctrl.save($event)"]')).click().then ->	
                return
												return
        browser.waitForAngular()
        #expect(element.all(By.css('.kanban-cell .scrumdo-boards-column')).get(1).element(By.xpath('.//*[normalize-space(text())=normalize-space("' + cardName + '")]')).isPresent()).toBe true
        return