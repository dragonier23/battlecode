#!/usr/bin/env perl
use strict;
use warnings;

use File::Basename qw(dirname);
use File::Copy qw(copy);
use File::Path qw(make_path);
use File::Spec;

my $script_dir = dirname(File::Spec->rel2abs($0));
my $bots_dir   = File::Spec->catdir($script_dir, 'bots');
my $common_dir = File::Spec->catdir($bots_dir, 'common');

my $bot_name = shift @ARGV;
if (!defined $bot_name) {
    die "Usage: perl sync.pl <bot-name>\n";
}

$bot_name =~ s/^\s+|\s+$//g;
if ($bot_name eq '') {
    die "Bot name cannot be empty.\n";
}

if ($bot_name =~ /[\\\/:*?\"<>|]/) {
    die "Bot name contains invalid characters for a directory name.\n";
}

if (!-d $common_dir) {
    die "Could not find common bot directory at: $common_dir\n";
}

if ($bot_name eq 'common') {
    die "Refusing to sync common into itself.\n";
}

my $target_dir = File::Spec->catdir($bots_dir, $bot_name);
if (!-d $target_dir) {
    die "Target bot directory does not exist: $target_dir\n";
}

copy_tree($common_dir, $target_dir);
print "Synced common files into bot '$bot_name'.\n";

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
