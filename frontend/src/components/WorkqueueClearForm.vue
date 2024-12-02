<template>
    <div class="workqueue-clear-form">
        <form @submit.prevent="clearWorkqueue">
            <div class="flex gap-0 mt-2 flex-wrap">
                <!-- Date field -->
                <div class="flex-1"> 
                    <label class="font-semibold">Older than:</label>               
                    <div class="relative max-w-md">
                        <input id="date" v-model="days_older_than" 
                        datepicker-format="dd-mm-yyyy" type="date"  
                        @click="openDatepicker"
                        class="input input-bordered w-full max-w-sm"
                        :max="maxDate">
                     
                    </div>
                </div>
                
                <!-- Status field -->
                 <div class="flex-1">
                    <label class="font-semibold">Itemstatus:</label>
                <div>              
                    <select v-model="workitem_status" class="select select-bordered w-full max-w-sm">              
                        <option value="">All</option>
                        <option value="new">New</option>
                        <option value="in progress">In progress</option>
                        <option value="completed">Completed</option>
                        <option value="failed">Failed</option>
                        <option value="pending user action">Pending user action</option>
                    </select>
                </div>
            </div>
        </div>
                <!-- Action Buttons -->
            <div class="flex justify-end space-x-2 mt-4">
                <button type="submit" class="btn btn-primary">Clear queue</button>
                <button type="button" @click="back" class="btn">Back</button>
            </div>
        </form>
    </div>
</template>

<script>
export default {
    name: 'WorkqueueClearForm',
    props: {
        workqueue: {
            type: Object,
            required: true
        }
    },
    data() {

        const today = new Date();
        const day = String(today.getDate()).padStart(2, '0');
        const month = String(today.getMonth() + 1).padStart(2, '0'); // months are 0-based
        const year = today.getFullYear();
        const formattedDate = `${year}-${month}-${day}`;
        const maxDate = `${year}-${month}-${day}`

        return {
            days_older_than: formattedDate,
            workitem_status : '',
            maxDate: maxDate
        };
    },
    methods: {
        clearWorkqueue() {
            var numberOfDays = this.calculateDaysOlderThan(this.days_older_than);
            this.$emit("clearWorkqueue", this.workqueue.id, this.workitem_status, numberOfDays);
        },
        isValidDate(dateString) {
            const regex = /^(0[1-9]|[12][0-9]|3[01])-(0[1-9]|1[0-2])-\d{4}$/;
            return regex.test(dateString);
        },
        calculateDaysOlderThan(dateString) {

            const [day, month, year] = dateString.split('-');
            const isoFormattedDate = `${day}-${month}-${year}`;
            const givenDate = new Date(isoFormattedDate);
            const currentDate = new Date();
            const timeDifference = currentDate - givenDate;
            const daysDifference = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
            console.log(daysDifference);
            return daysDifference;
        },
        openDatepicker(event) {
            // If the input type is date, triggering the click will open the datepicker
            event.target.showPicker();
        },
        back() {
      this.$emit('back');
    }
    }
};
</script>

<style scoped>
</style>

