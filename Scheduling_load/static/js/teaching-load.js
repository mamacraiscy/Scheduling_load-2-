$(document).ready(function() {
    // Toggle filter panel
    $('#filter-btn').click(function() {
        $('#filter-panel').toggleClass('active');
    });

    // Fetch suggestions as the user types in the search input
    $("#search-input").keyup(function() {
        var query = $(this).val();  // Get the search query
        var filter = $('input[name="filter"]:checked').val();  // Get the selected filter

        if (query.length > 1) {  // Trigger search if query length is greater than 1
            $.ajax({
                url: "{% url 'instructor_search' %}",  // Your search URL
                data: {
                    'q': query,
                    'filter': filter  // Pass the filter to backend
                },
                success: function(data) {
                    $("#suggestions").html('');  // Clear previous suggestions
                    if (data.results.length > 0) {
                        $("#suggestions").addClass('suggestions-visible');  // Show suggestions box
                        data.results.forEach(function(item) {
                            $("#suggestions").append('<div class="suggestion-item" data-id="' + item.id + '">' + item.name + '</div>');
                        });
                    } else {
                        $("#suggestions").removeClass('suggestions-visible');  // Hide suggestions box
                        $("#suggestions").append('<div class="suggestion-item">No suggestions found.</div>');
                    }
                },
                error: function(xhr, status, error) {
                    console.error("Error fetching suggestions:", error);
                    $("#suggestions").removeClass('suggestions-visible');  // Hide suggestions if error occurs
                }
            });
        } else {
            $("#suggestions").removeClass('suggestions-visible');  // Hide suggestions if no query
        }
    });

    // When a suggestion is clicked, fetch instructor details
    $(document).on('click', '.suggestion-item', function() {
        var instructorId = $(this).data('id');  // Get the instructor ID from the clicked suggestion
        $.ajax({
            url: "{% url 'instructor_details' %}",
            data: {
                'id': instructorId  // Send instructor ID to get detailed info
            },
            success: function(data) {
                $("#instructor-details").html(data.html);  // Populate the results pane with instructor details
                $("#suggestions").empty();  // Clear suggestions
                $("#search-input").val('');  // Clear the search input
            }
        });
    });

    // Hide suggestions when the search input loses focus
    $("#search-input").on('blur', function() {
        setTimeout(function() {
            $("#suggestions").removeClass('suggestions-visible');
            $("#suggestions").empty();
        }, 100);  // Delay to allow clicking on suggestion
    });
});
