// taken from http://ericnish.io/blog/compile-less-files-with-grunt

module.exports = function(grunt) {
  grunt.initConfig({
    less: {
      development: {
        options: {
          compress: true,
          yuicompress: true,
          optimization: 2
        },
        files: {
          // target.css file: source.less file
          "stronger/static/stronger/css/layout.css": "stronger/static/stronger/css/layout.less"
        }
      }
    },
    watch: {
      styles: {
        files: ['stronger/static/stronger/css/**/*.less'],
        tasks: ['less']
      }
    }
  });

  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-watch');

  grunt.registerTask('default', ['watch']);
};