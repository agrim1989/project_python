/// <reference path='../../_all.ts' />

module scrumdo {
    export class DatePickerController {
        public static $inject: Array<string> = [
            "$scope"
        ];

        public date: Date;
        public ngModel: ng.INgModelController;
        private MaxDate:Date;
        private MinDate:Date;

        constructor(public scope) {
            this.MaxDate = new Date(new Date().getFullYear() + 20, 1, 1);
            this.MinDate = new Date(new Date().getFullYear() - 10, 1, 1);
            
            this.scope.options = {
                opened: false,
                dateOptions: {
                    maxDate: this.MaxDate,
                    minDate: this.MinDate,
                    formatYear: 'yy',
                    startingDay: 1
                }
            };
            this.date = null;
            //this.scope.$watch('ctrl.date', this.changed);
        }

        formatDate(date, includePlaceholder = true) {
            if (date === null) {
                if (includePlaceholder && (this.scope.placeholder != null)) {
                    return this.scope.placeholder;
                }
                return '';
            }
            return moment(date).format('YYYY-MM-DD');
        }

        openPicker($event: MouseEvent) {
            trace("openDatePicker");
            $event.preventDefault();
            $event.stopPropagation();
            this.scope.options.opened = true;
            return
        }

        init(ngModel: ng.INgModelController) {
            this.ngModel = ngModel;
            this.date = ngModel.$modelValue === null ? null: this.parseDate(ngModel.$modelValue);
            this.ngModel.$render = () => {
                this.date = ngModel.$modelValue === null ? null: this.parseDate(ngModel.$modelValue);
            }
            return
        }

        // try to get Date object irrespective to User TimeZone
        parseDate(input) {
            try{
                var parts = input.match(/(\d+)/g);
                return new Date(parts[0], parseInt(parts[1])-1, parts[2]);
            }catch(e){
                trace("Not a valid Date");
                return null;
            }
        }

        changed = () => {
            var d = this.formatDate(this.date, false);
            if (d !== '') {
                this.ngModel.$setViewValue(d);
            } else {
                this.ngModel.$setViewValue(null);
            }
            return
        }
    }

}