import {MigrationInterface, QueryRunner} from "typeorm";

export class AutoreplyPrimaryKeyRefactor1542108653161 implements MigrationInterface {

    public async up(queryRunner: QueryRunner): Promise<any> {
        await queryRunner.query(`ALTER TABLE "autoreply" DROP CONSTRAINT "PK_ddc41824c974ba54b637996bb1e"`);
        await queryRunner.query(`ALTER TABLE "autoreply" ADD CONSTRAINT "PK_96105d425fb2d6c94f313f99948" PRIMARY KEY ("pattern", "guild_id")`);
        await queryRunner.query(`ALTER TABLE "autoreply" DROP CONSTRAINT "FK_5de193cb109a0e9c71f54b82eab"`);
        await queryRunner.query(`ALTER TABLE "autoreply" ALTER COLUMN "guild_id" SET NOT NULL`);
        await queryRunner.query(`ALTER TABLE "autoreply" ADD CONSTRAINT "FK_5de193cb109a0e9c71f54b82eab" FOREIGN KEY ("guild_id") REFERENCES "guild"("id")`);
    }

    public async down(queryRunner: QueryRunner): Promise<any> {
        await queryRunner.query(`ALTER TABLE "autoreply" DROP CONSTRAINT "FK_5de193cb109a0e9c71f54b82eab"`);
        await queryRunner.query(`ALTER TABLE "autoreply" ALTER COLUMN "guild_id" DROP NOT NULL`);
        await queryRunner.query(`ALTER TABLE "autoreply" ADD CONSTRAINT "FK_5de193cb109a0e9c71f54b82eab" FOREIGN KEY ("guild_id") REFERENCES "guild"("id") ON DELETE NO ACTION ON UPDATE NO ACTION`);
        await queryRunner.query(`ALTER TABLE "autoreply" DROP CONSTRAINT "PK_96105d425fb2d6c94f313f99948"`);
        await queryRunner.query(`ALTER TABLE "autoreply" ADD CONSTRAINT "PK_ddc41824c974ba54b637996bb1e" PRIMARY KEY ("pattern")`);
    }

}
