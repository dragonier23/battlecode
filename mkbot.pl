#!/usr/bin/env perl
use strict;
use warnings;

use File::Basename qw(dirname);
use File::Copy qw(copy);
use File::Path qw(make_path);
use File::Spec;
use POSIX qw(strftime);

# Script location is used so this works no matter where it is run from.
my $script_dir = dirname(File::Spec->rel2abs($0));
my $bots_dir   = File::Spec->catdir($script_dir, 'bots');
my $common_dir = File::Spec->catdir($bots_dir, 'common');

if (!-d $common_dir) {
    die "Could not find common bot directory at: $common_dir\n";
}

print "Enter new bot name: ";
my $bot_name = <STDIN>;

defined $bot_name or die "No bot name provided.\n";
$bot_name =~ s/^\s+|\s+$//g;

if ($bot_name eq '') {
    die "Bot name cannot be empty.\n";
}

if ($bot_name =~ /[\\\/:*?\"<>|]/) {
    die "Bot name contains invalid characters for a directory name.\n";
}

my $target_dir = File::Spec->catdir($bots_dir, $bot_name);

if (-e $target_dir) {
    die "Target already exists: $target_dir\n";
}

copy_tree($common_dir, $target_dir);

my $strat_file = File::Spec->catfile($target_dir, 'strat.txt');
open my $fh, '>', $strat_file or die "Could not write $strat_file: $!\n";
my $timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime);
print {$fh} "# This bot is created at $timestamp\n";
close $fh;

print "Created bot '$bot_name' at: $target_dir\n";
print "Wrote strategy file: $strat_file\n";

sub copy_tree {
    my ($src, $dst) = @_;

    make_path($dst) unless -d $dst;

    opendir(my $dh, $src) or die "Could not open directory $src: $!\n";
    my @entries = grep { $_ ne '.' && $_ ne '..' } readdir($dh);
    closedir($dh);

    for my $entry (@entries) {
        my $src_path = File::Spec->catfile($src, $entry);
        my $dst_path = File::Spec->catfile($dst, $entry);

        if (-d $src_path) {
            copy_tree($src_path, $dst_path);
        } elsif (-f $src_path) {
            copy($src_path, $dst_path)
              or die "Could not copy $src_path to $dst_path: $!\n";
        }
    }
}
