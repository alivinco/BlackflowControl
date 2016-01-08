+function ($) {

  $(function(){
      var toggles = localStorage.getItem("toggles")
		if (!toggles) {
		  toggles = {".app":true}
		} else {
		  toggles = JSON.parse(toggles)
		}
	  if (!toggles[".app"]) {
		 $(".app").addClass("app-aside-folded")
	  } else {
		 $(".app").removeClass("app-aside-folded")
	  }
	  //console.dir($(".app"))
      $(document).on('click', '[ui-toggle-class]', function (e) {
        e.preventDefault();
        var $this = $(e.target);
        $this.attr('ui-toggle-class') || ($this = $this.closest('[ui-toggle-class]'));
        
		var classes = $this.attr('ui-toggle-class').split(','),
			targets = ($this.attr('target') && $this.attr('target').split(',')) || Array($this),
			key = 0;

		$.each(classes, function( index, value ) {

			var target = targets[(targets.length && key)];
			$( target ).toggleClass(classes[index]);
			//localStorage.setItem(target,classes[index])
			if (toggles[target])
				{toggles[target] = false}
			else
				{toggles[target] = true}
			key ++;
		});
		localStorage.setItem("toggles",JSON.stringify(toggles))
		$this.toggleClass('active');

      });
  });
}(jQuery);
