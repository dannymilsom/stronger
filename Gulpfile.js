// Core dependencies
var gulp = require('gulp'),
    path = require('path');

// Gulp plugin dependencies
var concat = require('gulp-concat'),
    minifycss = require('gulp-minify-css'),
    sass = require('gulp-sass');

// Base static directories
var static_dir = path.join('src', 'stronger', 'static', 'stronger'),
    sass_dir = path.join(static_dir, 'sass'),
    css_dir = path.join(static_dir, 'css'),
    js_dir = path.join(static_dir, 'js');

// SASS paths
var scss_src = path.join(sass_dir, 'layout.scss');

// Compile SASS to CSS
gulp.task('styles', function() {
    gulp.src(scss_src)
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest(css_dir));
});

// Vendor and site specific styling source paths
var styles_src = [
    path.join(css_dir, 'libs', 'font-awesome.css'),
    path.join(css_dir, 'libs', 'bootstrap.min.css'),
    path.join(css_dir, 'libs', 'select2.css'),
    path.join(css_dir, 'libs', 'jquery-ui.css'),
    path.join(css_dir, 'libs', 'source-sans-pro.css'),
    path.join(css_dir, 'layout.css')
]

// Concat styles
gulp.task('concat-styles', function() {
    gulp.src(styles_src)
        .pipe(concat({ path: 'styles.css'}))
        .pipe(gulp.dest(css_dir));
});

// Vendor and site specific script source path
var scripts_src = [
    path.join(js_dir, 'libs', 'jquery-1.11.1.min.js'),
    path.join(js_dir, 'libs', 'jquery-migrate-1.2.1.min.js'),
    path.join(js_dir, 'libs', 'jquery-ui.min.js'),
    path.join(js_dir, 'libs', 'jquery.validate.min.js'),
    path.join(js_dir, 'libs', 'additional-methods.min.js'),
    path.join(js_dir, 'libs', 'select2.min.js'),
    path.join(js_dir, 'libs', 'highchart.js'),
    path.join(js_dir, 'libs', 'highchart-exporting.js'),
    path.join(js_dir, 'stronger.js')
]

// Concat scripts
gulp.task('concat-scripts', function() {
    gulp.src(scripts_src)
        .pipe(concat({ path: 'scripts.js'}))
        .pipe(gulp.dest(js_dir));
});

gulp.task('default',function() {
    gulp.watch(scss_src,['styles']);
});

gulp.task('build', ['styles', 'concat-styles', 'concat-scripts',])
